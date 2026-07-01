import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../models/estacion.dart';
import 'login_screen.dart';
import 'add_estacion_screen.dart';
import 'detalles_estacion_screen.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late Future<List<Estacion>> futureEstaciones;

  @override
  void initState() {
    super.initState();
    futureEstaciones = ApiService().fetchEstaciones();
  }

  void _actualizarDatos() {
    setState(() {
      futureEstaciones = ApiService().fetchEstaciones();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Estaciones SMAT'),
        backgroundColor: Colors.blueAccent,
        foregroundColor: Colors.white,
        actions: [
          // BOTÓN DE CERRAR SESIÓN [cite: 958-968]
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await AuthService().logout();
              if (!mounted) return;
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(builder: (context) => const LoginScreen()),
                (route) => false,
              );
            },
          ),
        ],
      ),
      body: FutureBuilder<List<Estacion>>(
        future: futureEstaciones,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('❌ Error: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('No hay estaciones registradas.'));
          } else {
            return ListView.builder(
              itemCount: snapshot.data!.length,
              itemBuilder: (context, index) {
                final est = snapshot.data![index];
                // Importa la pantalla arriba: import 'detalles_estacion_screen.dart';

              return ListTile(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => DetallesEstacionScreen(estacion: est),
                    ),
                  );
                },
                leading: const Icon(Icons.satellite_alt, color: Colors.blueGrey),
                title: Text(est.nombre, style: const TextStyle(fontWeight: FontWeight.bold)),
                subtitle: Text(est.ubicacion),
                trailing: const Icon(Icons.chevron_right),
              );
              },
            );
          }
        },
      ),
      floatingActionButton: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          FloatingActionButton(
            heroTag: "btn1",
            onPressed: _actualizarDatos,
            child: const Icon(Icons.refresh),
          ),
          const SizedBox(height: 10),
          FloatingActionButton(
            heroTag: "btn2",
            backgroundColor: Colors.green,
            onPressed: () async {
              // Abrimos el formulario y esperamos a ver si guardó algo
              bool? refresh = await Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const AddEstacionScreen()),
              );
              if (refresh == true) _actualizarDatos();
            },
            child: const Icon(Icons.add, color: Colors.white),
          ),
        ],
      ),
    );
  }
}