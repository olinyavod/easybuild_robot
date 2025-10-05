import 'package:hive_ce/hive.dart';
import 'package:injectable/injectable.dart';

import 'package:easybuild_bot/hive/models.dart';

@singleton
class UsersService {
  final Box<BotUser> _usersBox;

  UsersService(this._usersBox);

  Future<void> addUser(BotUser user) async {
    await _usersBox.add(user);
  }

  Future<BotUser?> getUser(String userId) async {
    return _usersBox.get(userId);
  }

  Future<BotUser?> getUserByUserId(int userId) async {
    for(final user in _usersBox.values) {
      if(user.userId == userId) {
        return user;
      }
    }
    return null;
  }

  Future<List<BotUser>> getAllUsers() async {
    return _usersBox.values.toList();
  }
}