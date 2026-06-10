class Lectura {
  final int id;
  final double valor;
  final String fecha;

  Lectura({required this.id, required this.valor, required this.fecha});

  factory Lectura.fromJson(Map<String, dynamic> json) {
    return Lectura(
      id: json['id'],
      valor: json['valor'].toDouble(),
      fecha: json['fecha'] ?? DateTime.now().toString(),
    );
  }
}