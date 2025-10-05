import 'package:hive_ce/hive.dart';

part 'bot_user.g.dart';

@HiveType(typeId: 0)
class BotUser extends HiveObject{
  @HiveField(0)
  final String id;
  
  @HiveField(1)
  final int userId;
  
  @HiveField(2)
  String userName;
  
  @HiveField(3)
  String? displayName;
  
  @HiveField(4)
  bool allowed;

  @HiveField(5)
  bool isAdmin;

  BotUser({
    required this.id,
    required this.userId, 
    required this.userName, 
    this.displayName,
    this.allowed = false,
    this.isAdmin = false
  });
}