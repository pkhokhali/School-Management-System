import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';

final darkModeProvider = StateNotifierProvider<DarkModeNotifier, bool>((ref) {
  return DarkModeNotifier();
});

class DarkModeNotifier extends StateNotifier<bool> {
  DarkModeNotifier() : super(false) {
    final box = Hive.box('settings');
    state = box.get('dark_mode', defaultValue: true);
  }

  void toggle() {
    state = !state;
    Hive.box('settings').put('dark_mode', state);
  }
}
