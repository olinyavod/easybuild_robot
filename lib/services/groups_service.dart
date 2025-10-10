import 'package:hive_ce/hive.dart';
import 'package:injectable/injectable.dart';

import 'package:easybuild_bot/hive/models.dart';

@singleton
class GroupsService {
  final Box<BotGroup> _groupsBox;

  GroupsService(this._groupsBox);

  Future<void> addGroup(BotGroup group) async {
    await _groupsBox.add(group);
  }

  Future<BotGroup?> getGroup(String groupId) async {
    return _groupsBox.get(groupId);
  }

  Future<BotGroup?> getGroupByGroupId(int groupId) async {
    for(final group in _groupsBox.values) {
      if(group.groupId == groupId) {
        return group;
      }
    }
    return null;
  }

  Future<List<BotGroup>> getAllGroups() async {
    return _groupsBox.values.toList();
  }
}

