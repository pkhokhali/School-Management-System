import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api/api_client.dart';

class AdminDashboard extends ConsumerWidget {
  const AdminDashboard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return FutureBuilder(
      future: ref.read(dioProvider).get('/analytics/dashboard/'),
      builder: (context, snapshot) {
        final data = snapshot.data?.data ?? {};
        return Scaffold(
          appBar: AppBar(title: const Text('Admin Overview')),
          body: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              _StatCard('Students', '${data['total_students'] ?? 0}'),
              _StatCard('Pending Enrollments', '${data['pending_enrollments'] ?? 0}'),
              _StatCard('Fee Collected', 'NPR ${data['fee_collected'] ?? 0}'),
              _StatCard('Overdue', '${data['overdue_fees'] ?? 0}'),
            ],
          ),
        );
      },
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  const _StatCard(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(title: Text(label), trailing: Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold))),
    );
  }
}
