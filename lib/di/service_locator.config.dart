// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format width=80

// **************************************************************************
// InjectableConfigGenerator
// **************************************************************************

// ignore_for_file: type=lint
// coverage:ignore-file

// ignore_for_file: no_leading_underscores_for_library_prefixes
import 'package:easybuild_bot/di/external_modules.dart' as _i739;
import 'package:easybuild_bot/easybuild_bot.dart' as _i856;
import 'package:easybuild_bot/hive/models.dart' as _i39;
import 'package:easybuild_bot/services/services.dart' as _i995;
import 'package:easybuild_bot/services/users_service.dart' as _i93;
import 'package:get_it/get_it.dart' as _i174;
import 'package:hive_ce/hive.dart' as _i738;
import 'package:injectable/injectable.dart' as _i526;

extension GetItInjectableX on _i174.GetIt {
  // initializes the registration of main-scope dependencies inside of GetIt
  Future<_i174.GetIt> init({
    String? environment,
    _i526.EnvironmentFilter? environmentFilter,
  }) async {
    final gh = _i526.GetItHelper(this, environment, environmentFilter);
    final externalModules = _$ExternalModules();
    await gh.singletonAsync<_i738.Box<_i39.BotUser>>(
      () => externalModules.usersBox,
      preResolve: true,
    );
    gh.singleton<_i93.UsersService>(
      () => _i93.UsersService(gh<_i738.Box<_i39.BotUser>>()),
    );
    gh.singleton<_i856.EasybuildBot>(
      () => _i856.EasybuildBot(
        gh<String>(instanceName: 'botToken'),
        gh<_i995.UsersService>(),
      ),
    );
    return this;
  }
}

class _$ExternalModules extends _i739.ExternalModules {}
