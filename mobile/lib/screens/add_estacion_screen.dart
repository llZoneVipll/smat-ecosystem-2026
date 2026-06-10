import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AddEstacionScreen extends StatefulWidget {
  const AddEstacionScreen({super.key});

  @override
  State<AddEstacionScreen> createState() => _AddEstacionScreenState();
}

class _AddEstacionScreenState extends State<AddEstacionScreen> {
  final _nombreController = TextEditingController();
  final _ubicacionController = TextEditingController();
  bool _isSaving = false;

  void _guardarEstacion() async {
    if (_nombreController.text.isEmpty || _ubicacionController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Por favor, completa todos los campos')),
      );
      return;
    }

    setState(() => _isSaving = true);
    
    // Llamamos al método protegido que creamos en el ApiService
    bool success = await ApiService().crearEstacion(
      _nombreController.text,
      _ubicacionController.text,
    );

    setState(() => _isSaving = false);

    if (success) {
      if (!mounted) return;
      Navigator.pop(context, true); // Volver atrás avisando que hubo éxito
    } else {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error al guardar. ¿Sesión expirada?')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nueva Estación SMAT')),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            TextField(
              controller: _nombreController,
              decoration: const InputDecoration(labelText: 'Nombre de la Estación (Ej: Estación Rímac)'),
            ),
            TextField(
              controller: _ubicacionController,
              decoration: const InputDecoration(labelText: 'Ubicación / Coordenadas'),
            ),
            const SizedBox(height: 30),
            _isSaving
                ? const CircularProgressIndicator()
                : ElevatedButton.icon(
                    onPressed: _guardarEstacion,
                    icon: const Icon(Icons.save),
                    label: const Text('Guardar Estación'),
                  ),
          ],
        ),
      ),
    );
  }
}