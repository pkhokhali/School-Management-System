import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api/api_client.dart';
import '../../core/providers/feature_provider.dart';

class FeesScreen extends ConsumerWidget {
  const FeesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final online = isFeatureEnabled(ref.watch(featureFlagsProvider).valueOrNull, 'payments_online');
    return FutureBuilder(
      future: ref.read(dioProvider).get('/fees/assignments/'),
      builder: (context, snapshot) {
        if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
        final list = snapshot.data!.data['results'] ?? snapshot.data!.data as List;
        return ListView.builder(
          itemCount: list.length,
          itemBuilder: (_, i) {
            final f = list[i];
            return Card(
              child: ListTile(
                title: Text('NPR ${f['total_amount']}'),
                subtitle: Text('Paid: ${f['paid_amount']} — ${f['status']}'),
                trailing: online
                    ? TextButton(child: const Text('Pay'), onPressed: () {})
                    : null,
              ),
            );
          },
        );
      },
    );
  }
}
