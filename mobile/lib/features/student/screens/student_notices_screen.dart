import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/student_palette.dart';
import '../data/student_providers.dart';
import '../widgets/student_ui.dart';

class StudentNoticesScreen extends ConsumerWidget {
  const StudentNoticesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final announcements = ref.watch(studentAnnouncementsProvider);

    return Scaffold(
      backgroundColor: StudentPalette.surface,
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          StudentNavyHeader(
            title: 'Notices',
            subtitle: 'Announcements from your institute',
            trailing: IconButton(
              onPressed: () => Navigator.pop(context),
              icon: const Icon(Icons.close, color: Colors.white70),
            ),
          ),
          Expanded(
            child: announcements.when(
              loading: () => const Center(child: CircularProgressIndicator(color: StudentPalette.indigo)),
              error: (e, _) => Center(child: Text('$e')),
              data: (list) => RefreshIndicator(
                color: StudentPalette.indigo,
                onRefresh: () async => ref.invalidate(studentAnnouncementsProvider),
                child: ListView(
                  padding: const EdgeInsets.all(14),
                  children: list.isEmpty
                      ? [const Text('No notices', style: TextStyle(color: StudentPalette.textMuted))]
                      : list.map((a) {
                          return StudentCard(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        a['title']?.toString() ?? 'Notice',
                                        style: const TextStyle(
                                          fontWeight: FontWeight.w700,
                                          fontSize: 13,
                                          color: StudentPalette.textPrimary,
                                        ),
                                      ),
                                    ),
                                    if (a['is_read'] == false)
                                      const StudentPill('New', type: StudentPillType.blue),
                                  ],
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  a['body']?.toString() ?? '',
                                  style: const TextStyle(fontSize: 11, color: StudentPalette.textMuted),
                                ),
                              ],
                            ),
                          );
                        }).toList(),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
