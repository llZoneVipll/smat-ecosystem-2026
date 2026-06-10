import 'package:flutter/material.dart';
import '../models/estacion.dart';
import '../models/lectura.dart';
import '../services/api_service.dart';
import 'widgets/sensor_chart_widget.dart'; // Importa el widget

class DetallesEstacionScreen extends StatelessWidget {
  final Estacion estacion;
  const DetallesEstacionScreen({super.key, required this.estacion});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(estacion.nombre)),
      body: FutureBuilder<List<Lectura>>(
        future: ApiService().fetchHistorial(estacion.id),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
          
          final historial = snapshot.data ?? [];

          return Column(
            children: [
              // RESUMEN DE ALERTA
              if (historial.isNotEmpty) _buildStatusCard(historial.last.valor),

              // GRÁFICO DE TENDENCIA
              if (historial.length > 1) 
                SensorChartWidget(historial: historial)
              else
                const Padding(padding: EdgeInsets.all(20), child: Text("Faltan datos para generar gráfico")),

              const Divider(),
              const Text('📜 Historial Reciente', style: TextStyle(fontWeight: FontWeight.bold)),
              
              Expanded(
                child: ListView.builder(
                  itemCount: historial.length,
                  itemBuilder: (context, index) {
                    final lectura = historial[index];
                    return ListTile(
                      dense: true,
                      leading: const Icon(Icons.history),
                      title: Text('Valor: ${lectura.valor}'),
                      subtitle: Text(lectura.fecha),
                    );
                  },
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildStatusCard(double valor) {
    Color color = Colors.green;
    String status = "ESTADO: NORMAL";
    if (valor > 50) { color = Colors.red; status = "⚠️ PELIGRO CRÍTICO"; }
    else if (valor > 30) { color = Colors.orange; status = "🔸 ALERTA"; }

    return Card(
      color: color,
      margin: const EdgeInsets.all(15),
      child: ListTile(
        title: Text(status, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        subtitle: Text('Última lectura: $valor', style: const TextStyle(color: Colors.white70)),
      ),
    );
  }
}