import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers/feature_provider.dart';
import '../../../core/theme/student_palette.dart';
import '../data/student_providers.dart';
import '../widgets/student_ui.dart';

class StudentFeesTab extends ConsumerWidget {
  const StudentFeesTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final online = isFeatureEnabled(ref.watch(featureFlagsProvider).valueOrNull, 'payments_online');
    final fees = ref.watch(studentFeesProvider);

    return fees.when(
      loading: () => const Center(child: CircularProgressIndicator(color: StudentPalette.mint)),
      error: (e, _) => Center(child: Text('Error: $e')),
      data: (list) {
        var due = 0.0;
        var paid = 0.0;
        var total = 0.0;
        String? nearestDue;
        for (final f in list) {
          final bal = double.tryParse('${f['balance']}') ?? 0;
          final p = double.tryParse('${f['paid_amount']}') ?? 0;
          final t = double.tryParse('${f['net_amount'] ?? f['total_amount']}') ?? 0;
          due += bal;
          paid += p;
          total += t;
          if (bal > 0 && f['due_date'] != null) nearestDue ??= f['due_date']?.toString();
        }
        final pctPaid = total > 0 ? (paid / total * 100).clamp(0, 100) : 0.0;

        return RefreshIndicator(
          color: StudentPalette.mint,
          onRefresh: () async => ref.invalidate(studentFeesProvider),
          child: ListView(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
            children: [
              const Text(
                'Fees & Payments',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600, color: StudentPalette.textPrimary),
              ),
              const SizedBox(height: 12),
              if (due > 0 && nearestDue != null)
                Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.warning_amber_rounded, color: Color(0xFFF87171), size: 22),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Fee deadline approaching',
                              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFFF87171)),
                            ),
                            Text(
                              'Due date: $nearestDue',
                              style: const TextStyle(fontSize: 11, color: StudentPalette.textMuted),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: StudentPalette.teal.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Total Due', style: TextStyle(fontSize: 11, color: StudentPalette.textMuted)),
                            Text(
                              'NPR ${due.toStringAsFixed(0)}',
                              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w700, color: Colors.white),
                            ),
                          ],
                        ),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            const Text('Paid', style: TextStyle(fontSize: 11, color: StudentPalette.textMuted)),
                            Text(
                              'NPR ${paid.toStringAsFixed(0)}',
                              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: Color(0xFF4ADE80)),
                            ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    StudentProgressBar(percent: pctPaid.toDouble(), color: StudentPalette.mint),
                    const SizedBox(height: 4),
                    Text(
                      '${pctPaid.round()}% of fees paid',
                      style: const TextStyle(fontSize: 11, color: StudentPalette.textMuted),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              const StudentSectionTitle('Breakdown'),
              if (list.isEmpty)
                const Text('No fee assignments', style: TextStyle(color: StudentPalette.textMuted))
              else
                ...list.map((f) {
                  final bal = double.tryParse('${f['balance']}') ?? 0;
                  final status = f['status']?.toString() ?? '';
                  final chip = bal <= 0
                      ? const StudentStatusChip('Paid', color: Color(0xFF4ADE80), bg: Color(0x3322C55E))
                      : status.contains('partial')
                          ? const StudentStatusChip('Part', color: Color(0xFFFBBF24), bg: Color(0x33F0A500))
                          : const StudentStatusChip('Due', color: Color(0xFFF87171), bg: Color(0x33EF4444));
                  return StudentDarkRow(
                    icon: Icons.receipt_long_outlined,
                    iconBg: StudentPalette.teal.withValues(alpha: 0.25),
                    title: f['fee_head_name']?.toString() ?? 'Fee',
                    subtitle: f['due_date']?.toString() ?? status,
                    trailing: Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        chip,
                        Text(
                          'NPR ${(f['net_amount'] ?? f['total_amount']).toString()}',
                          style: const TextStyle(fontSize: 11, color: StudentPalette.textMuted),
                        ),
                      ],
                    ),
                  );
                }),
              if (online && due > 0) ...[
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Fonepay — connect gateway in admin settings')),
                    );
                  },
                  style: FilledButton.styleFrom(
                    backgroundColor: StudentPalette.mint,
                    foregroundColor: StudentPalette.bgDark,
                    minimumSize: const Size.fromHeight(48),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('Pay Now via Fonepay  →', style: TextStyle(fontWeight: FontWeight.w700)),
                ),
              ],
            ],
          ),
        );
      },
    );
  }
}
