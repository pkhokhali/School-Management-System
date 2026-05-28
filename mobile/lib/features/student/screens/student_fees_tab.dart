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
      loading: () => const Center(child: CircularProgressIndicator(color: StudentPalette.indigo)),
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

        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            StudentNavyHeader(
              title: '₹ ${due.toStringAsFixed(0)}',
              subtitle: total > 0
                  ? 'Outstanding · ${pctPaid.round()}% paid of ₹${total.toStringAsFixed(0)}'
                  : 'Fees & payments',
              trailing: Navigator.canPop(context)
                  ? IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.arrow_back, color: Colors.white70),
                    )
                  : null,
              stats: [
                (value: '₹${paid.toStringAsFixed(0)}', label: 'Paid', valueColor: const Color(0xFF4ADE80)),
                (value: '₹${due.toStringAsFixed(0)}', label: 'Due', valueColor: const Color(0xFFF87171)),
                (
                  value: nearestDue != null ? nearestDue!.split('-').skip(1).join('/') : '—',
                  label: 'Deadline',
                  valueColor: const Color(0xFFFBBF24),
                ),
              ],
            ),
            if (due > 0 && nearestDue != null)
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 14),
                child: StudentAlertBanner(
                  title: 'Fee deadline approaching',
                  subtitle: 'Late fee may apply after due date',
                ),
              ),
            Expanded(
              child: RefreshIndicator(
                color: StudentPalette.indigo,
                onRefresh: () async => ref.invalidate(studentFeesProvider),
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(14, 12, 14, 24),
                  children: [
                    const StudentSectionHeader(title: 'Breakdown'),
                    if (list.isEmpty)
                      const Text('No fee assignments', style: TextStyle(color: StudentPalette.textMuted))
                    else
                      ...list.map((f) {
                        final bal = double.tryParse('${f['balance']}') ?? 0;
                        final status = f['status']?.toString() ?? '';
                        final pill = bal <= 0
                            ? const StudentPill('Paid ✓', type: StudentPillType.green)
                            : status.contains('partial')
                                ? const StudentPill('Partial', type: StudentPillType.amber)
                                : const StudentPill('Due', type: StudentPillType.red);
                        return StudentCard(
                          child: Row(
                            children: [
                              StudentIconBox(
                                icon: bal <= 0 ? Icons.check : Icons.receipt_long_outlined,
                                bg: bal <= 0 ? StudentPalette.successBg : StudentPalette.errorBg,
                                iconColor: bal <= 0 ? StudentPalette.success : StudentPalette.error,
                                size: 28,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      f['fee_head_name']?.toString() ?? 'Fee',
                                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                                    ),
                                    Text(
                                      f['due_date']?.toString() ?? status,
                                      style: const TextStyle(fontSize: 10, color: StudentPalette.textMuted),
                                    ),
                                  ],
                                ),
                              ),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  Text(
                                    '₹${(f['net_amount'] ?? f['total_amount']).toString()}',
                                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800),
                                  ),
                                  pill,
                                ],
                              ),
                            ],
                          ),
                        );
                      }),
                    if (online && due > 0) ...[
                      const SizedBox(height: 8),
                      StudentPrimaryButton(
                        label: 'Pay via Fonepay',
                        icon: Icons.phone_android,
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Fonepay — connect gateway in admin settings')),
                          );
                        },
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}
