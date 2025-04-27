# AI Powered traffic-management System

This repository contains a Traffic Management System that utilizes **YOLOv8** for vehicle detection and **MiDaS** for depth estimation to dynamically adjust traffic signal timings based on vehicle density, queue length, and depth information. The goal is to optimize traffic flow and reduce congestion at intersections.

## Project Overview

This system detects vehicles, estimates traffic density, and dynamically adjusts traffic light timings. The system also uses depth information from **MiDaS** to determine the queue length and congestion level, helping to provide real-time control for traffic signals.

### Key Features:
- **Vehicle Detection:** Using YOLOv8 to detect vehicles in real-time.
- **Traffic Density Estimation:** Calculating vehicle count and queue length on each side of the intersection.
- **Dynamic Signal Adjustment:** Adjusting traffic signal timings based on real-time traffic density.
- **Depth Estimation:** Leveraging MiDaS to estimate the depth of vehicles, providing more accurate traffic flow management.
