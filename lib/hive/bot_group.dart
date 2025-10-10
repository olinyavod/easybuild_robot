import 'package:hive_ce/hive.dart';

part 'bot_group.g.dart';

@HiveType(typeId: 1)
class BotGroup extends HiveObject{
  @HiveField(0)
  final String id;
  
  @HiveField(1)
  final int groupId;
  
  @HiveField(2)
  String groupName;

  BotGroup({
    required this.id,
    required this.groupId, 
    required this.groupName,
  });
}

