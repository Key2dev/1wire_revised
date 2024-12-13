#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cmath>
#include <chrono>
#include <thread>
#include <filesystem>

namespace fs = std::filesystem;

class OneWireReader {
private:
    const std::string base_dir = "/sys/bus/w1/devices/";

    std::vector<std::string> find_temp_sensors() {
        std::vector<std::string> sensors;
        for (const auto & entry : fs::directory_iterator(base_dir)) {
            if (entry.path().filename().string().substr(0, 2) == "28") {
                sensors.push_back(entry.path().string());
            }
        }
        return sensors;
    }

    std::vector<std::string> read_temp_raw(const std::string& device_file) {
        std::vector<std::string> lines;
        std::ifstream file(device_file);
        std::string line;
        while (std::getline(file, line)) {
            lines.push_back(line);
        }
        return lines;
    }

    float read_1wire_sensor(const std::string& sensor) {
        while (true) {
            auto lines = read_temp_raw(sensor + "/w1_slave");
            if (lines.size() >= 2 && lines[0].substr(lines[0].length() - 3) == "YES") {
                size_t pos = lines[1].find("t=");
                if (pos != std::string::npos) {
                    std::string temp_string = lines[1].substr(pos + 2);
                    return std::round(std::stof(temp_string) / 1000.0 * 100.0) / 100.0;
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(200));
        }
    }

public:
    std::vector<float> read_1wire_sensors() {
        std::vector<float> temps;
        auto temp_sensors = find_temp_sensors();
        for (const auto& sensor : temp_sensors) {
            temps.push_back(read_1wire_sensor(sensor));
        }
        return temps;
    }
};

int main() {
    OneWireReader reader;
    auto temperatures = reader.read_1wire_sensors();
    
    for (size_t i = 0; i < temperatures.size(); ++i) {
        std::cout << "Sensor " << i + 1 << ": " << temperatures[i] << "°C" << std::endl;
    }

    return 0;
}