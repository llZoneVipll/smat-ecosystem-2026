import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/estacion.dart';
import 'auth_service.dart';
import '../models/lectura.dart';

class ApiService {
  final String baseUrl = "http://127.0.0.1:8000";

  // Endpoint público
  Future<List<Estacion>> fetchEstaciones() async {
    final response = await http.get(Uri.parse('$baseUrl/estaciones/'));

    if (response.statusCode == 200) {
      List jsonResponse = json.decode(response.body);
      return jsonResponse.map((data) => Estacion.fromJson(data)).toList();
    } else {
      throw Exception('Error al conectar con el servidor SMAT');
    }
  }

Future<List<Lectura>> fetchHistorial(int estacionId) async {
    final response = await http.get(Uri.parse('$baseUrl/estaciones/$estacionId/historial'));

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = json.decode(response.body);
      List jsonResponse = data['historial'];
      return jsonResponse.map((l) => Lectura.fromJson(l)).toList();
    } else {
      return []; // Devolvemos lista vacía si no hay lecturas
    }
  }
  
  // Endpoint protegido
  Future<bool> crearEstacion(String nombre, String ubicacion) async {
    final token = await AuthService().getToken();

    final response = await http.post(
      Uri.parse('$baseUrl/estaciones/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'nombre': nombre, 'ubicacion': ubicacion}),
    );

    return response.statusCode == 201 || response.statusCode == 200;
  }
}