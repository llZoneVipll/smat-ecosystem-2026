import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import '../../models/lectura.dart';

class SensorChartWidget extends StatelessWidget {
  final List<Lectura> historial;
  const SensorChartWidget({super.key, required this.historial});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 200,
      padding: const EdgeInsets.all(10),
      child: LineChart(
        LineChartData(
          gridData: const FlGridData(show: false),
          titlesData: const FlTitlesData(show: false),
          borderData: FlBorderData(show: true, border: Border.all(color: Colors.blueGrey, width: 1)),
          lineBarsData: [
            LineChartBarData(
              spots: historial.asMap().entries.map((e) {
                return FlSpot(e.key.toDouble(), e.value.valor);
              }).toList(),
              isCurved: true,
              color: Colors.blueAccent,
              barWidth: 3,
              belowBarData: BarAreaData(show: true, color: Colors.blueAccent.withOpacity(0.2)),
            ),
          ],
        ),
      ),
    );
  }
}