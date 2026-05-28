import 'package:flutter/material.dart';
import '../../../core/theme/student_palette.dart';

// —— Header (navy band per mockup) ——

class StudentNavyHeader extends StatelessWidget {
  const StudentNavyHeader({
    super.key,
    required this.title,
    this.subtitle,
    this.trailing,
    this.bottom,
    this.stats,
    this.chips,
  });

  final String title;
  final String? subtitle;
  final Widget? trailing;
  final Widget? bottom;
  final List<({String value, String label, Color? valueColor})>? stats;
  final List<Widget>? chips;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
      decoration: const BoxDecoration(
        color: StudentPalette.navy,
        borderRadius: BorderRadius.vertical(bottom: Radius.circular(0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w800,
                        color: Colors.white,
                        letterSpacing: -0.3,
                      ),
                    ),
                    if (subtitle != null)
                      Padding(
                        padding: const EdgeInsets.only(top: 2),
                        child: Text(
                          subtitle!,
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.white.withValues(alpha: 0.45),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
              if (trailing != null) trailing!,
            ],
          ),
          if (chips != null && chips!.isNotEmpty) ...[
            const SizedBox(height: 10),
            Row(children: chips!),
          ],
          if (stats != null && stats!.isNotEmpty) ...[
            const SizedBox(height: 12),
            Row(
              children: [
                for (var i = 0; i < stats!.length; i++) ...[
                  if (i > 0) const SizedBox(width: 6),
                  Expanded(child: _StatBox(stats![i])),
                ],
              ],
            ),
          ],
          if (bottom != null) ...[const SizedBox(height: 10), bottom!],
        ],
      ),
    );
  }
}

class _StatBox extends StatelessWidget {
  const _StatBox(this.item);

  final ({String value, String label, Color? valueColor}) item;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        children: [
          Text(
            item.value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w800,
              color: item.valueColor ?? Colors.white,
            ),
          ),
          Text(
            item.label,
            style: TextStyle(
              fontSize: 9,
              fontWeight: FontWeight.w600,
              color: Colors.white.withValues(alpha: 0.4),
            ),
          ),
        ],
      ),
    );
  }
}

// —— Body cards ——

class StudentCard extends StatelessWidget {
  const StudentCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(11),
    this.margin = const EdgeInsets.only(bottom: 7),
    this.onTap,
    this.borderLeft,
  });

  final Widget child;
  final EdgeInsets padding;
  final EdgeInsets margin;
  final VoidCallback? onTap;
  final Color? borderLeft;

  @override
  Widget build(BuildContext context) {
    Widget card = Container(
      margin: margin,
      padding: padding,
      decoration: BoxDecoration(
        color: StudentPalette.white,
        borderRadius: BorderRadius.only(
          topRight: const Radius.circular(12),
          bottomRight: const Radius.circular(12),
          topLeft: borderLeft != null ? Radius.zero : const Radius.circular(12),
          bottomLeft: borderLeft != null ? Radius.zero : const Radius.circular(12),
        ),
        border: Border(
          left: borderLeft != null
              ? BorderSide(color: borderLeft!, width: 3)
              : const BorderSide(color: StudentPalette.cardBorder, width: 0.5),
          top: const BorderSide(color: StudentPalette.cardBorder, width: 0.5),
          right: const BorderSide(color: StudentPalette.cardBorder, width: 0.5),
          bottom: const BorderSide(color: StudentPalette.cardBorder, width: 0.5),
        ),
      ),
      child: child,
    );
    if (onTap != null) {
      card = Material(
        color: Colors.transparent,
        child: InkWell(onTap: onTap, child: card),
      );
    }
    return card;
  }
}

class StudentSectionHeader extends StatelessWidget {
  const StudentSectionHeader({super.key, required this.title, this.action});

  final String title;
  final Widget? action;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Expanded(
            child: Text(
              title,
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w700,
                color: StudentPalette.textPrimary,
              ),
            ),
          ),
          if (action != null) action!,
        ],
      ),
    );
  }
}

class StudentSectionTitle extends StatelessWidget {
  const StudentSectionTitle(this.label, {super.key});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Text(
        label.toUpperCase(),
        style: const TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.5,
          color: StudentPalette.textMuted,
        ),
      ),
    );
  }
}

class StudentProgressBar extends StatelessWidget {
  const StudentProgressBar({super.key, required this.percent, this.color});

  final double percent;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final c = color ?? StudentPalette.progressColor(percent);
    return ClipRRect(
      borderRadius: BorderRadius.circular(4),
      child: LinearProgressIndicator(
        value: (percent / 100).clamp(0, 1),
        minHeight: 5,
        backgroundColor: StudentPalette.grayBg,
        color: c,
      ),
    );
  }
}

enum StudentPillType { green, blue, amber, red, purple, gray }

class StudentPill extends StatelessWidget {
  const StudentPill(this.label, {super.key, this.type = StudentPillType.blue});

  final String label;
  final StudentPillType type;

  @override
  Widget build(BuildContext context) {
    final (bg, fg) = switch (type) {
      StudentPillType.green => (StudentPalette.successBg, StudentPalette.successText),
      StudentPillType.blue => (StudentPalette.infoBg, StudentPalette.infoText),
      StudentPillType.amber => (StudentPalette.warningBg, StudentPalette.warningText),
      StudentPillType.red => (StudentPalette.errorBg, StudentPalette.errorText),
      StudentPillType.purple => (const Color(0xFFF3E8FF), StudentPalette.purple),
      StudentPillType.gray => (StudentPalette.grayBg, StudentPalette.grayText),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(20)),
      child: Text(
        label,
        style: TextStyle(fontSize: 9, fontWeight: FontWeight.w700, color: fg),
      ),
    );
  }
}

class StudentStatusChip extends StatelessWidget {
  const StudentStatusChip(this.label, {super.key, required this.color, required this.bg});

  final String label;
  final Color color;
  final Color bg;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(20)),
      child: Text(label, style: TextStyle(fontSize: 9, fontWeight: FontWeight.w700, color: color)),
    );
  }
}

class StudentIconBox extends StatelessWidget {
  const StudentIconBox({super.key, required this.icon, required this.bg, this.iconColor, this.size = 32});

  final IconData icon;
  final Color bg;
  final Color? iconColor;
  final double size;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(9)),
      child: Icon(icon, size: size * 0.45, color: iconColor ?? StudentPalette.textPrimary),
    );
  }
}

class StudentCourseRow extends StatelessWidget {
  const StudentCourseRow({
    super.key,
    required this.icon,
    required this.iconBg,
    required this.iconColor,
    required this.title,
    this.subtitle,
    this.pill,
    this.percent,
    this.barColor,
    this.onTap,
  });

  final IconData icon;
  final Color iconBg;
  final Color iconColor;
  final String title;
  final String? subtitle;
  final StudentPill? pill;
  final double? percent;
  final Color? barColor;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return StudentCard(
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              StudentIconBox(icon: icon, bg: iconBg, iconColor: iconColor),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: StudentPalette.textPrimary,
                      ),
                    ),
                    if (subtitle != null)
                      Text(
                        subtitle!,
                        style: const TextStyle(fontSize: 10, color: StudentPalette.textMuted),
                      ),
                  ],
                ),
              ),
              if (pill != null) pill!,
            ],
          ),
          if (percent != null) ...[
            const SizedBox(height: 7),
            StudentProgressBar(percent: percent!, color: barColor),
            const SizedBox(height: 4),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${percent!.round()}%',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: percent! >= 100 ? StudentPalette.success : StudentPalette.textPrimary,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

class StudentQuickGrid extends StatelessWidget {
  const StudentQuickGrid({super.key, required this.items});

  final List<({IconData icon, String label, VoidCallback onTap})> items;

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      crossAxisCount: 4,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 8,
      crossAxisSpacing: 8,
      childAspectRatio: 0.85,
      children: items.map((item) {
        return Material(
          color: StudentPalette.white,
          borderRadius: BorderRadius.circular(12),
          child: InkWell(
            onTap: item.onTap,
            borderRadius: BorderRadius.circular(12),
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: StudentPalette.cardBorder, width: 0.5),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(item.icon, color: StudentPalette.indigo, size: 22),
                  const SizedBox(height: 4),
                  Text(
                    item.label,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 9,
                      fontWeight: FontWeight.w600,
                      color: StudentPalette.textPrimary,
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}

class StudentPrimaryButton extends StatelessWidget {
  const StudentPrimaryButton({super.key, required this.label, this.onPressed, this.icon});

  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: FilledButton(
        onPressed: onPressed,
        style: FilledButton.styleFrom(
          backgroundColor: StudentPalette.indigo,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (icon != null) ...[Icon(icon, size: 18), const SizedBox(width: 6)],
            Text(label, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 13)),
          ],
        ),
      ),
    );
  }
}

class StudentAlertBanner extends StatelessWidget {
  const StudentAlertBanner({super.key, required this.title, this.subtitle, this.warning = true});

  final String title;
  final String? subtitle;
  final bool warning;

  @override
  Widget build(BuildContext context) {
    final bg = warning ? const Color(0xFFFFF7ED) : StudentPalette.infoBg;
    final border = warning ? const Color(0xFFFED7AA) : StudentPalette.infoBg;
    final fg = warning ? const Color(0xFFC2410C) : StudentPalette.infoText;
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: bg,
        border: Border.all(color: border, width: 0.5),
        borderRadius: BorderRadius.circular(9),
      ),
      child: Row(
        children: [
          Icon(warning ? Icons.warning_amber_rounded : Icons.info_outline, color: fg, size: 18),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: fg)),
                if (subtitle != null)
                  Text(subtitle!, style: TextStyle(fontSize: 11, color: fg.withValues(alpha: 0.85))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// Legacy wrappers
class StudentHeroCard extends StatelessWidget {
  const StudentHeroCard({super.key, required this.stats});

  final List<({String value, String label})> stats;

  @override
  Widget build(BuildContext context) {
    return StudentNavyHeader(
      title: 'Your week',
      subtitle: 'At a glance',
      stats: stats
          .map((s) => (value: s.value, label: s.label, valueColor: null as Color?))
          .toList(),
    );
  }
}

class StudentQuickAction extends StatelessWidget {
  const StudentQuickAction({
    super.key,
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: StudentPalette.white,
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: StudentPalette.cardBorder),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, color: StudentPalette.indigo, size: 22),
              const SizedBox(height: 4),
              Text(
                label,
                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: StudentPalette.textPrimary),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class StudentDarkRow extends StatelessWidget {
  const StudentDarkRow({
    super.key,
    required this.icon,
    required this.iconBg,
    required this.title,
    this.subtitle,
    this.trailing,
    this.child,
    this.onTap,
  });

  final IconData icon;
  final Color iconBg;
  final String title;
  final String? subtitle;
  final Widget? trailing;
  final Widget? child;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return StudentCard(
      onTap: onTap,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          StudentIconBox(icon: icon, bg: iconBg, iconColor: StudentPalette.indigo),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: StudentPalette.textPrimary),
                ),
                if (subtitle != null)
                  Text(subtitle!, style: const TextStyle(fontSize: 10, color: StudentPalette.textMuted)),
                if (child != null) ...[const SizedBox(height: 6), child!],
              ],
            ),
          ),
          if (trailing != null) trailing!,
        ],
      ),
    );
  }
}

String studentGreeting() {
  final h = DateTime.now().hour;
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
}

String initials(String name) {
  final parts = name.trim().split(RegExp(r'\s+'));
  if (parts.isEmpty) return '?';
  if (parts.length == 1) return parts.first.substring(0, 1).toUpperCase();
  return '${parts.first[0]}${parts.last[0]}'.toUpperCase();
}
