import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/api/api_client.dart';

class NoticesScreen extends ConsumerWidget {
  const NoticesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return FutureBuilder(
      future: ref.read(dioProvider).get('/announcements/'),
      builder: (context, snapshot) {
        if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
        final list = snapshot.data!.data['results'] ?? snapshot.data!.data as List;
        return ListView.builder(
          itemCount: list.length,
          itemBuilder: (_, i) {
            final a = list[i];
            return ListTile(
              title: Text(a['title']),
              subtitle: Text(a['body']?.toString().substring(0, 80) ?? ''),
              trailing: a['is_read'] == false ? const Icon(Icons.fiber_new, color: Colors.blue) : null,
            );
          },
        );
      },
    );
  }
}
