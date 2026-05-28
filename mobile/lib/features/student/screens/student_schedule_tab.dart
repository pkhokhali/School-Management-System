import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api/api_client.dart';
import '../../../core/theme/student_palette.dart';
import '../widgets/student_ui.dart';

final _scheduleMonthProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final now = DateTime.now();
  final res = await ref.read(dioProvider).get(
    '/events/calendar/month/',
    queryParameters: {'year': now.year, 'month': now.month},
  );
  final data = res.data;
  if (data is List) {
    return data.map((e) => Map<String, dynamic>.from(e as Map)).toList();
  }
  if (data is Map && data['events'] is List) {
    return (data['events'] as List).map((e) => Map<String, dynamic>.from(e as Map)).toList();
  }
  return [];
});

class StudentScheduleTab extends ConsumerWidget {
  const StudentScheduleTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final events = ref.watch(_scheduleMonthProvider);
    final now = DateTime.now();
    final weekLabel =
        'Week of ${_monthDay(now)} – ${_monthDay(now.add(const Duration(days: 4)))}';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        StudentNavyHeader(
          title: 'Schedule',
          subtitle: weekLabel,
          bottom: _WeekDayPicker(selected: now.weekday),
        ),
        Expanded(
          child: events.when(
            loading: () => const Center(child: CircularProgressIndicator(color: StudentPalette.indigo)),
            error: (e, _) => Center(child: Text('Could not load schedule\n$e', textAlign: TextAlign.center)),
            data: (list) {
              final today = list.where((e) {
                final d = e['date']?.toString() ?? e['start_date']?.toString() ?? '';
                return d.startsWith('${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}');
              }).toList();

              return RefreshIndicator(
                color: StudentPalette.indigo,
                onRefresh: () async => ref.invalidate(_scheduleMonthProvider),
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(14, 12, 14, 24),
                  children: [
                    if (today.isNotEmpty) ...[
                      Row(
                        children: [
                          Container(width: 2, height: 28, color: StudentPalette.error),
                          const SizedBox(width: 8),
                          const Text(
                            'Today',
                            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: StudentPalette.error),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      ...today.asMap().entries.map((entry) {
                        final i = entry.key;
                        final e = entry.value;
                        final colors = [StudentPalette.info, StudentPalette.purple, StudentPalette.success, const Color(0xFFEA580C)];
                        final c = colors[i % colors.length];
                        return StudentCard(
                          borderLeft: c,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Expanded(
                                    child: Text(
                                      e['title']?.toString() ?? 'Event',
                                      style: const TextStyle(
                                        fontSize: 12,
                                        fontWeight: FontWeight.w700,
                                        color: StudentPalette.textPrimary,
                                      ),
                                    ),
                                  ),
                                  if (i == 0) const StudentPill('Live', type: StudentPillType.red),
                                  if (i == 1) const StudentPill('Next', type: StudentPillType.amber),
                                ],
                              ),
                              Text(
                                e['description']?.toString() ?? e['location']?.toString() ?? '',
                                style: const TextStyle(fontSize: 10, color: StudentPalette.textMuted),
                              ),
                              if (e['start_time'] != null)
                                Padding(
                                  padding: const EdgeInsets.only(top: 4),
                                  child: Text(
                                    '${e['start_time']} – ${e['end_time'] ?? ''}',
                                    style: const TextStyle(fontSize: 10, color: StudentPalette.textMuted),
                                  ),
                                ),
                            ],
                          ),
                        );
                      }),
                    ] else ...[
                      const StudentAlertBanner(
                        title: 'No classes scheduled today',
                        subtitle: 'Check the academic calendar for upcoming events',
                        warning: false,
                      ),
                      ...list.take(8).map((e) {
                        return StudentCard(
                          child: ListTile(
                            contentPadding: EdgeInsets.zero,
                            title: Text(
                              e['title']?.toString() ?? 'Event',
                              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
                            ),
                            subtitle: Text(
                              e['date']?.toString() ?? '',
                              style: const TextStyle(fontSize: 10),
                            ),
                          ),
                        );
                      }),
                    ],
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  static String _monthDay(DateTime d) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return '${months[d.month - 1]} ${d.day}';
  }
}

class _WeekDayPicker extends StatelessWidget {
  const _WeekDayPicker({required this.selected});

  final int selected;

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final start = now.subtract(Duration(days: now.weekday - 1));
    const labels = ['MON', 'TUE', 'WED', 'THU', 'FRI'];
    return Row(
      children: List.generate(5, (i) {
        final d = start.add(Duration(days: i));
        final isSel = d.weekday == selected;
        return Expanded(
          child: Container(
            margin: EdgeInsets.only(right: i < 4 ? 3 : 0),
            padding: const EdgeInsets.symmetric(vertical: 6),
            decoration: BoxDecoration(
              color: isSel ? StudentPalette.indigo : Colors.white.withValues(alpha: 0.07),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              children: [
                Text(
                  labels[i],
                  style: TextStyle(
                    fontSize: 9,
                    fontWeight: FontWeight.w700,
                    color: isSel ? Colors.white70 : Colors.white38,
                  ),
                ),
                Text(
                  '${d.day}',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                    color: isSel ? Colors.white : Colors.white54,
                  ),
                ),
              ],
            ),
          ),
        );
      }),
    );
  }
}
