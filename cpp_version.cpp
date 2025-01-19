#include <iostream>
#define _USE_MATH_DEFINES
#include <cmath>
// #include <unordered_set>
#include <set>
#include <unordered_map>
#include <vector>
#include <algorithm>
#include <chrono>
#include <iterator>

using idx_t = size_t;
using fp_t = double;
inline constexpr double DEFAULT_PROXIMITY_THRESHOLD = 1e-09;

inline constexpr bool is_near(fp_t a, fp_t b, fp_t threshold = DEFAULT_PROXIMITY_THRESHOLD) {
    return std::abs(a - b) < threshold;
}

struct Point {
    fp_t x;
    fp_t y;
};

struct Graph {
    std::vector<Point> points;
    std::unordered_map<idx_t, std::set<idx_t>> connections;
};

struct PolygonEntry {
    idx_t first_vertex_idx;
    idx_t last_vertex_idx;
};

std::ostream& operator<<(std::ostream& stream, const Point& point) {
    stream << "(" << point.x << " ; " << point.y << ")";
    return stream;
}

// Saves the polygon data
void save_polygon_elements(Graph& graph, std::vector<PolygonEntry>& polygons_list, const std::vector<Point>& polygon) {
    idx_t num_vertices = polygon.size();
    idx_t first_vertex_idx = graph.points.size();

    // Register all the vertices of the polygon
    graph.points.insert(graph.points.end(), polygon.begin(), polygon.end());

    // Save polygon points indices for Stage 4
    polygons_list.push_back({ first_vertex_idx, first_vertex_idx + num_vertices - 1 });

    for (idx_t begin_vertex_index = 0; begin_vertex_index < num_vertices; begin_vertex_index++) {
        // Get IDs (indices in the points list)
        idx_t begin_vertex_idx = first_vertex_idx + begin_vertex_index;
        idx_t end_vertex_index = (begin_vertex_index + 1) % num_vertices;
        idx_t end_vertex_idx = first_vertex_idx + end_vertex_index;

        // Initialize the sets, if the keys are not yet present
        // graph.connections.setdefault(begin_vertex_id, set());
        // graph.connections.setdefault(end_vertex_id, set());

        // Connect together
        graph.connections[begin_vertex_idx].insert(end_vertex_idx);
        graph.connections[end_vertex_idx].insert(begin_vertex_idx);
    }
}

std::vector<std::vector<Point>> compute_polygons(const std::vector<Point>& polygon_centers, fp_t polygon_radius, unsigned char number_of_vertices) {
    std::vector<std::vector<Point>> polygons{};
    polygons.reserve(polygon_centers.size());

    for (const Point& center : polygon_centers) {
        std::vector<Point> polygon{};
        polygon.reserve(number_of_vertices);

        for (idx_t vertex_index = 0; vertex_index < number_of_vertices; vertex_index++) {
            fp_t angle = vertex_index * 2 * M_PI / number_of_vertices;
            Point new_vertex = { center.x + polygon_radius * std::cos(angle), center.y + polygon_radius * std::sin(angle) };
            polygon.push_back(new_vertex);
        }

        polygons.push_back(std::move(polygon));
    }

    return std::move(polygons);
}

constexpr bool segments_intersect(const Point& a, const Point& b, const Point& c, const Point& d, bool ignore_endpoint_proximity=false) {
    // https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
    fp_t denominator = (a.x - b.x) * (c.y - d.y) - (a.y - b.y) * (c.x - d.x);
    if (denominator == 0) { // The lines are parallel
        return false;
    }

    Point intersection = {
        ((a.x * b.y - a.y * b.x) * (c.x - d.x) - (a.x - b.x) * (c.x * d.y - c.y * d.x)) / denominator,
        ((a.x * b.y - a.y * b.x) * (c.y - d.y) - (a.y - b.y) * (c.x * d.y - c.y * d.x)) / denominator
    };

    // my own genius from this point on
    // compute vectors (ab), (ap), (cd), (cp), where p is the intersection point
    // (ab) || (ap) & (cd) || (cp)
    // (ap) = m * (ab) ; if m <= 1 ==> p belongs to (ab) }
    // (cp) = n * (cd) ; if n <= 1 ==> p belongs to (cd) } => count the intersection

    Point ab_vec = { b.x - a.x, b.y - a.y };
    Point ap_vec = { intersection.x - a.x, intersection.y - a.y };
    fp_t m = (!is_near(ab_vec.x, 0)) ? ap_vec.x / ab_vec.x : ap_vec.y / ab_vec.y;
    Point cd_vec = { d.x - c.x, d.y - c.y };
    Point cp_vec = { intersection.x - c.x, intersection.y - c.y };
    fp_t n = (!is_near(cd_vec.x, 0)) ? cp_vec.x / cd_vec.x : cp_vec.y / cd_vec.y;

    bool intersection_close_to_endpoints = is_near(m, 0) || is_near(m, 1) || is_near(n, 0) || is_near(n, 1);
    if (0 < m && m <= 1 && 0 < n && n <= 1 && (!ignore_endpoint_proximity || !intersection_close_to_endpoints)) {
        return true;
        /*
        # Code below replaced by the 3rd condition of the if statement above.
        # if not ignore_endpoint_proximity:
        #     return True
        #
        # if ignore_endpoint_proximity and not intersection_close_to_endpoints:
        #     return True
        */
    }

    return false;
}

bool segment_intersects_any(const Graph& graph, idx_t a_idx, idx_t b_idx) {
    for (idx_t c_idx = 0; c_idx < graph.points.size(); c_idx++) {
        for (idx_t d_idx : graph.connections.at(c_idx)) {
            // If there exists the connection c <-> d, then there also exists d <-> c
            // If d_idx is less than c_idx, such connection has already been handled since the loop got to d_idx first
            if (d_idx < c_idx) {
                continue;
            }

            // The segments share at least one endpoint, obviously do intersect
            if (a_idx == c_idx || a_idx == d_idx || b_idx == c_idx || b_idx == d_idx) {
                continue;
            }

            if (segments_intersect(graph.points[a_idx], graph.points[b_idx], graph.points[c_idx], graph.points[d_idx])) {
                return true;
            }
        }
    }

    return false;
}

Graph generate_mesh(const std::vector<Point>& polygon_centers, fp_t polygon_radius, unsigned char number_of_vertices) {
    Graph graph{};
    std::vector<PolygonEntry> polygons{};  // A helper list for Stage 4

    // Stage 1: Save a rectangle as polygon data
    save_polygon_elements(graph, polygons, {
        {0, 0},
        {0, 1},
        {1, 1},
        {1, 0}
    });

    // Stage 2: Save polygon data
    auto pols = compute_polygons(polygon_centers, polygon_radius, number_of_vertices);
    for (const auto& polygon : pols) {
        save_polygon_elements(graph, polygons, polygon);
    }

    // Stage 3: Compute primary segments
    for (idx_t rectangle_vertex_idx = 0; rectangle_vertex_idx < 4; rectangle_vertex_idx++) {
        for (idx_t point_idx = 4; point_idx < graph.points.size(); point_idx++) {
            if (segment_intersects_any(graph, rectangle_vertex_idx, point_idx)) {
                continue;
            }

            graph.connections[rectangle_vertex_idx].insert(point_idx);
            graph.connections[point_idx].insert(rectangle_vertex_idx);
        }
    }

    // Stage 4: Compute secondary segments
    auto complete_triangle = [&] (idx_t starting_idx) {
        for (idx_t a_idx = starting_idx; a_idx < graph.points.size(); a_idx++) {
            for (idx_t b_idx : graph.connections.at(a_idx)) {
                // Look for a 3rd point to complete the triangle
                std::vector<idx_t> potential_c_idxs{};
                std::set_difference(graph.connections[a_idx].begin(), graph.connections[a_idx].end(), graph.connections[b_idx].begin(), graph.connections[b_idx].end(), std::inserter(potential_c_idxs, potential_c_idxs.begin()));
                for (idx_t c_idx : potential_c_idxs) {
                    if (c_idx == b_idx) {
                        continue;
                    }
                    // Prevents connections inside the polygons from forming
                    if (std::any_of(polygons.begin(), polygons.end(), [&b_idx, &c_idx](const PolygonEntry& polygon) {
                        return polygon.first_vertex_idx <= b_idx && b_idx <= polygon.last_vertex_idx && polygon.first_vertex_idx <= c_idx && c_idx <= polygon.last_vertex_idx;
                    })) {
                        continue;
                    }
                    if (segment_intersects_any(graph, a_idx, c_idx) || segment_intersects_any(graph, b_idx, c_idx)) {
                        continue;
                    }
                    graph.connections[b_idx].insert(c_idx);
                    graph.connections[c_idx].insert(b_idx);
                    return std::pair<bool, idx_t>{ false, a_idx };
                }
            }
        }
        return std::pair<bool, idx_t>{ true, 0 };
    };

    idx_t starting_idx = 0;
    while (true) {
        auto [done, new_idx] = complete_triangle(starting_idx);
        if (done) {
            break;
        }
        starting_idx = new_idx;
    }

    return graph;
}

int main() {
    std::vector<Point> polygon_centers = {
        { 0.6, 0.8 },
        { 0.5, 0.5 },
        { 0.7, 0.4 }
    };
    fp_t radius = 0.1;
    unsigned char vertices = 6;

    auto start = std::chrono::high_resolution_clock::now();

    Graph mesh = generate_mesh(polygon_centers, radius, vertices);

    std::cout << "elapsed time: " << ((std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock::now() - start)).count() / 1'000'000.0);

    std::cout << "ms\nnum points: " << mesh.points.size() << "\n";

    return 0;
}
