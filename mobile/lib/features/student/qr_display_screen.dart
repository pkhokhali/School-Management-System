import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../../core/api/api_client.dart';

class QRDisplayScreen extends ConsumerWidget {
  const QRDisplayScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return FutureBuilder(
      future: ref.read(dioProvider).get('/students/'),
      builder: (context, snapshot) {
        if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
        final list = snapshot.data!.data['results'] ?? snapshot.data!.data as List;
        if (list.isEmpty) return const Center(child: Text('No profile'));
        final student = list.first;
        return FutureBuilder(
          future: ref.read(dioProvider).get('/students/${student['id']}/qr/'),
          builder: (context, snap2) {
            if (!snap2.hasData) return const CircularProgressIndicator();
            final payload = snap2.data!.data['payload'] as String;
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  QrImageView(data: payload, size: 220),
                  const SizedBox(height: 16),
                  Text(student['enrollment_number'] ?? '', style: Theme.of(context).textTheme.titleMedium),
                ],
              ),
            );
          },
        );
      },
    );
  }
}
