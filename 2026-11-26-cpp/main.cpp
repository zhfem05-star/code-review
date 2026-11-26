#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <mutex>
#include <sstream>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>

// access log 한 줄 형식: <timestamp> <method> <path> <status> <latency_ms>
struct Stats {
    std::unordered_map<int, long> status_count;
    std::unordered_map<std::string, long> path_count;
    long latency_sum = 0;
    long processed = 0;
};

class LogAggregator {
public:
    explicit LogAggregator(unsigned num_workers) : num_workers_(num_workers) {}

    void run(const std::vector<std::string>& lines) {
        std::vector<std::thread> workers;
        size_t chunk = lines.size() / num_workers_;
        for (unsigned w = 0; w < num_workers_; ++w) {
            size_t begin = w * chunk;
            size_t end = begin + chunk;
            workers.emplace_back([this, lines, begin, end] {
                for (size_t i = begin; i < end; ++i) {
                    process_line(lines[i]);
                }
            });
        }
        for (auto& t : workers) {
            t.join();
        }
    }

    void print_report(size_t top_n) const {
        std::cout << "processed lines: " << stats_.processed << "\n";
        std::map<int, long> by_status(stats_.status_count.begin(), stats_.status_count.end());
        for (const auto& [status, cnt] : by_status) {
            std::cout << "  status " << status << ": " << cnt << "\n";
        }
        if (stats_.processed > 0) {
            std::cout << "avg latency(ms): " << stats_.latency_sum / stats_.processed << "\n";
        }

        std::vector<std::pair<std::string, long>> paths(stats_.path_count.begin(), stats_.path_count.end());
        size_t n = std::min(top_n, paths.size());
        std::partial_sort(paths.begin(), paths.begin() + n, paths.end(),
                          [](const auto& a, const auto& b) { return a.second > b.second; });
        std::cout << "top " << n << " paths:\n";
        for (size_t i = 0; i < n; ++i) {
            std::cout << "  " << paths[i].first << " (" << paths[i].second << ")\n";
        }
    }

private:
    void process_line(const std::string& line) {
        std::istringstream iss(line);
        std::string ts, method, path, status_str, latency_str;
        if (!(iss >> ts >> method >> path >> status_str >> latency_str)) {
            return;  // 필드가 모자란 줄은 건너뜀
        }
        int status = std::stoi(status_str);
        long latency = std::stol(latency_str);

        stats_.path_count[path]++;

        std::lock_guard<std::mutex> lock(mu_);
        stats_.status_count[status]++;
        stats_.latency_sum += latency;
        stats_.processed++;
    }

    unsigned num_workers_;
    Stats stats_;
    std::mutex mu_;
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "usage: " << argv[0] << " <access_log_path>\n";
        return 1;
    }
    std::ifstream in(argv[1]);
    std::vector<std::string> lines;
    std::string line;
    while (std::getline(in, line)) {
        lines.push_back(line);
    }

    LogAggregator agg(std::thread::hardware_concurrency());
    agg.run(lines);
    agg.print_report(3);
    return 0;
}
