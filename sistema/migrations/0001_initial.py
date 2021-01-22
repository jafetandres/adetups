# Generated by Django 3.1.2 on 2021-01-22 01:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('foto', models.ImageField(blank=True, default='img_perfil/default-avatar.jpg', null=True, upload_to='img_perfil')),
                ('nombres', models.CharField(blank=True, max_length=50, null=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('apellidos', models.CharField(blank=True, max_length=50, null=True)),
                ('username', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(blank=True, default=True, null=True)),
                ('is_staff', models.BooleanField(blank=True, default=False, null=True)),
                ('tipo', models.CharField(blank=True, max_length=20, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Adtclascre',
            fields=[
                ('clccodigo', models.SmallAutoField(db_column='CLCCODIGO', primary_key=True, serialize=False)),
                ('clcdescri', models.CharField(db_column='CLCDESCRI', max_length=30)),
                ('clcvaldes', models.DecimalField(db_column='CLCVALDES', decimal_places=2, max_digits=6)),
                ('clcvalhas', models.DecimalField(db_column='CLCVALHAS', decimal_places=2, max_digits=6)),
                ('clcautori', models.CharField(db_column='CLCAUTORI', max_length=2)),
                ('clcestado', models.CharField(db_column='CLCESTADO', max_length=3)),
                ('clcusucre', models.CharField(db_column='CLCUSUCRE', max_length=15)),
                ('clcfeccre', models.DateTimeField(auto_now=True, db_column='CLCFECCRE')),
                ('clchorcre', models.CharField(db_column='CLCHORCRE', max_length=8)),
                ('clcusumod', models.CharField(blank=True, db_column='CLCUSUMOD', max_length=15, null=True)),
                ('clcfecmod', models.DateField(blank=True, db_column='CLCFECMOD', null=True)),
                ('clchormod', models.CharField(blank=True, db_column='CLCHORMOD', max_length=8, null=True)),
                ('clcplamax', models.SmallIntegerField(db_column='CLCPLAMAX')),
                ('clcgarant', models.CharField(db_column='CLCGARANT', max_length=2)),
            ],
            options={
                'db_table': 'ADTCLASCRE',
            },
        ),
        migrations.CreateModel(
            name='Adtclasol',
            fields=[
                ('csocodigo', models.SmallAutoField(db_column='CSOCODIGO', primary_key=True, serialize=False)),
                ('csoabrev', models.CharField(db_column='CSOABREV', max_length=5, unique=True)),
                ('csodescri', models.CharField(db_column='CSODESCRI', max_length=30)),
                ('csoestado', models.CharField(db_column='CSOESTADO', max_length=3)),
                ('csousucre', models.CharField(db_column='CSOUSUCRE', max_length=15)),
                ('csofeccre', models.DateTimeField(auto_now=True, db_column='CSOFECCRE')),
                ('csohorcre', models.CharField(db_column='CSOHORCRE', max_length=8)),
                ('csousumod', models.CharField(blank=True, db_column='CSOUSUMOD', max_length=15, null=True)),
                ('csofecmod', models.DateField(blank=True, db_column='CSOFECMOD', null=True)),
                ('csohormod', models.CharField(blank=True, db_column='CSOHORMOD', max_length=8, null=True)),
            ],
            options={
                'db_table': 'ADTCLASOL',
            },
        ),
        migrations.CreateModel(
            name='Adtcredito',
            fields=[
                ('crecodigo', models.BigAutoField(db_column='CRECODIGO', primary_key=True, serialize=False)),
                ('cresocio', models.CharField(db_column='CRESOCIO', max_length=10)),
                ('cremonto', models.DecimalField(db_column='CREMONTO', decimal_places=2, max_digits=9)),
                ('crecuota', models.DecimalField(db_column='CRECUOTA', decimal_places=2, max_digits=9)),
                ('creintere', models.DecimalField(db_column='CREINTERE', decimal_places=2, max_digits=4)),
                ('creplazo', models.SmallIntegerField(db_column='CREPLAZO')),
                ('crenrocob', models.SmallIntegerField(db_column='CRENROCOB')),
                ('crepagado', models.DecimalField(db_column='CREPAGADO', decimal_places=2, max_digits=9)),
                ('creestado', models.CharField(db_column='CREESTADO', max_length=3)),
                ('creusucre', models.CharField(db_column='CREUSUCRE', max_length=15)),
                ('crehorcre', models.CharField(db_column='CREHORCRE', max_length=8)),
                ('crefeccre', models.DateField(db_column='CREFECCRE')),
                ('creusumod', models.CharField(blank=True, db_column='CREUSUMOD', max_length=15, null=True)),
                ('crefecmod', models.DateField(blank=True, db_column='CREFECMOD', null=True)),
                ('crehormod', models.CharField(blank=True, db_column='CREHORMOD', max_length=8, null=True)),
                ('crependien', models.DecimalField(db_column='CREPENDIEN', decimal_places=2, max_digits=9)),
            ],
            options={
                'db_table': 'ADTCREDITO',
            },
        ),
        migrations.CreateModel(
            name='Adtparam',
            fields=[
                ('prmcodigo', models.CharField(db_column='PRMCODIGO', max_length=10, primary_key=True, serialize=False)),
                ('prmdescri', models.CharField(db_column='PRMDESCRI', max_length=100)),
                ('prmcarac', models.CharField(db_column='PRMCARAC', max_length=200)),
                ('prmnumer', models.DecimalField(db_column='PRMNUMER', decimal_places=2, max_digits=9)),
                ('prmfecha', models.DateField(db_column='PRMFECHA')),
                ('prmusucre', models.CharField(db_column='PRMUSUCRE', max_length=15)),
                ('prmfeccre', models.DateField(db_column='PRMFECCRE')),
                ('prmhorcre', models.CharField(db_column='PRMHORCRE', max_length=8)),
                ('prmusumod', models.CharField(blank=True, db_column='PRMUSUMOD', max_length=15, null=True)),
                ('prmfecmod', models.DateField(blank=True, db_column='PRMFECMOD', null=True)),
                ('prmhormod', models.CharField(blank=True, db_column='PRMHORMOD', max_length=8, null=True)),
                ('prmestado', models.CharField(db_column='PRMESTADO', max_length=3)),
            ],
            options={
                'db_table': 'ADTPARAM',
            },
        ),
        migrations.CreateModel(
            name='Adtperfil',
            fields=[
                ('percodigo', models.CharField(db_column='PERCODIGO', max_length=10, primary_key=True, serialize=False)),
                ('perdescri', models.CharField(db_column='PERDESCRI', max_length=25)),
                ('perestado', models.CharField(db_column='PERESTADO', max_length=3)),
                ('perusucre', models.CharField(db_column='PERUSUCRE', max_length=15)),
                ('perfeccre', models.DateField(blank=True, db_column='PERFECCRE', null=True)),
                ('perhorcre', models.CharField(blank=True, db_column='PERHORCRE', max_length=8, null=True)),
                ('perusumod', models.CharField(blank=True, db_column='PERUSUMOD', max_length=15, null=True)),
                ('perfecmod', models.DateField(blank=True, db_column='PERFECMOD', null=True)),
                ('perhormod', models.CharField(blank=True, db_column='PERHORMOD', max_length=8, null=True)),
            ],
            options={
                'db_table': 'ADTPERFIL',
            },
        ),
        migrations.CreateModel(
            name='Adtregistro',
            fields=[
                ('regcodigo', models.AutoField(db_column='REGCODIGO', primary_key=True, serialize=False)),
                ('regnombre', models.CharField(db_column='REGNOMBRE', max_length=20)),
                ('regcedrep', models.CharField(db_column='REGCEDREP', max_length=10)),
                ('regnomrep', models.CharField(db_column='REGNOMREP', max_length=100)),
                ('regfeccre', models.DateField(db_column='REGFECCRE')),
                ('reghorcre', models.CharField(db_column='REGHORCRE', max_length=8)),
                ('regcatego', models.SmallIntegerField(db_column='REGCATEGO')),
                ('regusucre', models.CharField(db_column='REGUSUCRE', max_length=15)),
            ],
            options={
                'db_table': 'ADTREGISTRO',
            },
        ),
        migrations.CreateModel(
            name='Adtrubros',
            fields=[
                ('rubcodigo', models.SmallAutoField(db_column='RUBCODIGO', primary_key=True, serialize=False)),
                ('rubabrev', models.CharField(db_column='RUBABREV', max_length=5, unique=True)),
                ('rubdescri', models.CharField(db_column='RUBDESCRI', max_length=50)),
                ('rubtipo', models.CharField(db_column='RUBTIPO', max_length=3)),
                ('rubestado', models.CharField(db_column='RUBESTADO', max_length=3)),
                ('rubusucre', models.CharField(db_column='RUBUSUCRE', max_length=15)),
                ('rubfeccre', models.DateField(db_column='RUBFECCRE')),
                ('rubhorcre', models.CharField(db_column='RUBHORCRE', max_length=8)),
                ('rubusumod', models.CharField(blank=True, db_column='RUBUSUMOD', max_length=15, null=True)),
                ('rubfecmod', models.DateField(blank=True, db_column='RUBFECMOD', null=True)),
                ('rubhormod', models.CharField(blank=True, db_column='RUBHORMOD', max_length=8, null=True)),
                ('rubvalor', models.DecimalField(db_column='RUBVALOR', decimal_places=2, max_digits=9)),
            ],
            options={
                'db_table': 'ADTRUBROS',
            },
        ),
        migrations.CreateModel(
            name='Adtsocios',
            fields=[
                ('soccodigo', models.AutoField(db_column='SOCCODIGO', primary_key=True, serialize=False)),
                ('soccedula', models.CharField(db_column='SOCCEDULA', max_length=10, unique=True)),
                ('socnombre', models.CharField(db_column='SOCNOMBRE', max_length=50)),
                ('socapelli', models.CharField(db_column='SOCAPELLI', max_length=50)),
                ('socdirecc', models.CharField(db_column='SOCDIRECC', max_length=80)),
                ('soctelefe', models.CharField(db_column='SOCTELEFE', max_length=15)),
                ('socmovil', models.CharField(db_column='SOCMOVIL', max_length=10)),
                ('socemail', models.CharField(db_column='SOCEMAIL', max_length=100)),
                ('soccargo', models.CharField(db_column='SOCCARGO', max_length=20)),
                ('socestado', models.CharField(db_column='SOCESTADO', max_length=3)),
                ('socusucre', models.CharField(blank=True, db_column='SOCUSUCRE', max_length=15, null=True)),
                ('socfeccre', models.DateField(db_column='SOCFECCRE')),
                ('sochorcre', models.CharField(db_column='SOCHORCRE', max_length=8)),
                ('socusumod', models.CharField(blank=True, db_column='SOCUSUMOD', max_length=15, null=True)),
                ('socfecmod', models.DateField(blank=True, db_column='SOCFECMOD', null=True)),
                ('sochormod', models.CharField(blank=True, db_column='SOCHORMOD', max_length=8, null=True)),
                ('socarea', models.CharField(db_column='SOCAREA', max_length=20)),
                ('socfecing', models.DateField(blank=True, db_column='SOCFECING', null=True)),
                ('soctiempo', models.SmallIntegerField(db_column='SOCTIEMPO')),
                ('socfoto', models.TextField(db_column='SOCFOTO')),
                ('socgenero', models.CharField(db_column='SOCGENERO', max_length=10)),
                ('soctipo', models.CharField(db_column='SOCTIPO', max_length=5)),
            ],
            options={
                'db_table': 'ADTSOCIOS',
            },
        ),
        migrations.CreateModel(
            name='ClaseCredito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(blank=True, max_length=30, null=True)),
                ('valdesde', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('valhasta', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('autorizacion', models.BooleanField(blank=True, default=True, null=True)),
                ('estado', models.CharField(blank=True, max_length=10, null=True)),
                ('plazomax', models.SmallIntegerField(blank=True, null=True)),
                ('garante', models.BooleanField(blank=True, default=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ClaseSolicitud',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=30)),
                ('estado', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Credito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=9)),
                ('cuota', models.DecimalField(decimal_places=2, max_digits=9)),
                ('interes', models.DecimalField(decimal_places=2, max_digits=4)),
                ('plazo', models.SmallIntegerField()),
                ('crenrocob', models.SmallIntegerField()),
                ('pagado', models.DecimalField(decimal_places=2, max_digits=9)),
                ('estado', models.CharField(db_column='CREESTADO', max_length=3)),
                ('pendiente', models.DecimalField(db_column='CREPENDIEN', decimal_places=2, max_digits=9)),
            ],
        ),
        migrations.CreateModel(
            name='Parametro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=100)),
                ('valorcaracter', models.CharField(max_length=200)),
                ('valornumerico', models.DecimalField(decimal_places=2, max_digits=9)),
                ('estado', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Rubro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=50)),
                ('tipo', models.CharField(max_length=3)),
                ('estado', models.CharField(max_length=3)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=9)),
            ],
        ),
        migrations.CreateModel(
            name='RubroSocio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(blank=True, max_length=20, null=True)),
                ('servicio', models.CharField(blank=True, max_length=100, null=True)),
                ('valor', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ('estado', models.CharField(blank=True, max_length=3, null=True)),
                ('fecha_ingreso', models.DateField(auto_now=True, null=True)),
                ('cuotas', models.CharField(blank=True, max_length=7, null=True)),
                ('rubro', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.rubro')),
            ],
        ),
        migrations.CreateModel(
            name='Socio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direccion', models.CharField(max_length=80)),
                ('telefono', models.CharField(max_length=15)),
                ('celular', models.CharField(max_length=10)),
                ('cargo', models.CharField(max_length=20)),
                ('area', models.CharField(max_length=20)),
                ('fecha_ingreso', models.DateField(blank=True, null=True)),
                ('is_garante', models.BooleanField(default=False)),
                ('rubros', models.ManyToManyField(blank=True, null=True, to='sistema.RubroSocio')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SolicitudCredito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_ingreso', models.DateTimeField(auto_now=True)),
                ('monto', models.DecimalField(decimal_places=2, max_digits=9)),
                ('plazo', models.SmallIntegerField()),
                ('estado', models.CharField(default='pendiente', max_length=20)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('clasecredito', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.clasecredito')),
                ('garante', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='garante', to='sistema.socio')),
                ('socio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='socio', to='sistema.socio')),
            ],
        ),
        migrations.CreateModel(
            name='RestriccionesCredito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plazomax', models.SmallIntegerField()),
                ('tiempodesde', models.SmallIntegerField()),
                ('tiempohasta', models.SmallIntegerField()),
                ('valhasta', models.DecimalField(decimal_places=2, max_digits=9)),
                ('estado', models.CharField(max_length=3)),
                ('clasecredito', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.clasecredito')),
            ],
        ),
        migrations.CreateModel(
            name='LiquidacionCredito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=9)),
                ('observacion', models.CharField(max_length=200)),
                ('estado', models.BooleanField(default=False)),
                ('documento', models.TextField()),
                ('credito', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.credito')),
            ],
        ),
        migrations.AddField(
            model_name='credito',
            name='socio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.socio'),
        ),
        migrations.AddField(
            model_name='credito',
            name='solicitud',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.clasesolicitud'),
        ),
        migrations.CreateModel(
            name='Adtusuario',
            fields=[
                ('usucodigo', models.AutoField(db_column='USUCODIGO', primary_key=True, serialize=False)),
                ('usuclave', models.CharField(db_column='USUCLAVE', max_length=80)),
                ('usuestado', models.CharField(db_column='USUESTADO', max_length=3)),
                ('usuusucre', models.CharField(db_column='USUUSUCRE', max_length=15)),
                ('usufeccre', models.DateField(db_column='USUFECCRE')),
                ('usuhorcre', models.CharField(db_column='USUHORCRE', max_length=8)),
                ('usuusumod', models.CharField(blank=True, db_column='USUUSUMOD', max_length=15, null=True)),
                ('usufecmod', models.DateField(blank=True, db_column='USUFECMOD', null=True)),
                ('usuhormod', models.CharField(blank=True, db_column='USUHORMOD', max_length=8, null=True)),
                ('percodigo', models.ForeignKey(db_column='PERCODIGO', on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.adtperfil')),
                ('soccodigo', models.ForeignKey(db_column='SOCCODIGO', on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.adtsocios')),
            ],
            options={
                'db_table': 'ADTUSUARIO',
            },
        ),
        migrations.CreateModel(
            name='Adtsolcre',
            fields=[
                ('solcodigo', models.BigAutoField(db_column='SOLCODIGO', primary_key=True, serialize=False)),
                ('solfeccre', models.DateTimeField(auto_now=True, db_column='SOLFECCRE')),
                ('solcedgar', models.CharField(db_column='SOLCEDGAR', max_length=10)),
                ('solmonto', models.DecimalField(db_column='SOLMONTO', decimal_places=2, max_digits=9)),
                ('solplazo', models.SmallIntegerField(db_column='SOLPLAZO')),
                ('solestado', models.CharField(db_column='SOLESTADO', default='tramite', max_length=10)),
                ('solcuota', models.DecimalField(db_column='SOLCUOTA', decimal_places=2, max_digits=9)),
                ('solintere', models.DecimalField(db_column='SOLINTERE', decimal_places=2, max_digits=9)),
                ('solporint', models.DecimalField(db_column='SOLPORINT', decimal_places=2, max_digits=4)),
                ('clccodigo', models.ForeignKey(db_column='CLCCODIGO', on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.adtclascre')),
                ('csocodigo', models.ForeignKey(db_column='CSOCODIGO', on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.adtclasol')),
                ('soccodigo', models.ForeignKey(db_column='SOCCODIGO', on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.adtsocios')),
            ],
            options={
                'db_table': 'ADTSOLCRE',
            },
        ),
        migrations.CreateModel(
            name='Adtrubsoc',
            fields=[
                ('rsocodigo', models.BigAutoField(db_column='RSOCODIGO', primary_key=True, serialize=False)),
                ('rsosocio', models.CharField(db_column='RSOSOCIO', max_length=10)),
                ('rsoanio', models.SmallIntegerField(db_column='RSOANIO')),
                ('rsomes', models.CharField(db_column='RSOMES', max_length=2)),
                ('rsovalor', models.DecimalField(db_column='RSOVALOR', decimal_places=2, max_digits=9)),
                ('rsorubro', models.CharField(db_column='RSORUBRO', max_length=5)),
                ('rsoestado', models.CharField(db_column='RSOESTADO', max_length=3)),
                ('rsofeccre', models.DateField(db_column='RSOFECCRE')),
                ('rsohorcre', models.CharField(db_column='RSOHORCRE', max_length=8)),
                ('rsousucre', models.CharField(db_column='RSOUSUCRE', max_length=15)),
                ('rsorefere', models.CharField(blank=True, db_column='RSOREFERE', max_length=10, null=True)),
                ('rubcodigo', models.ForeignKey(db_column='RUBCODIGO', on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.adtrubros')),
            ],
            options={
                'db_table': 'ADTRUBSOC',
            },
        ),
        migrations.CreateModel(
            name='Adtliqcre',
            fields=[
                ('liqcodigo', models.AutoField(db_column='LIQCODIGO', primary_key=True, serialize=False)),
                ('liqvalor', models.DecimalField(db_column='LIQVALOR', decimal_places=2, max_digits=9)),
                ('liqobserv', models.CharField(db_column='LIQOBSERV', max_length=200)),
                ('liqestado', models.CharField(db_column='LIQESTADO', max_length=3)),
                ('liqusucre', models.CharField(db_column='LIQUSUCRE', max_length=15)),
                ('liqfeccre', models.DateField(db_column='LIQFECCRE')),
                ('liqhorcre', models.CharField(db_column='LIQHORCRE', max_length=10)),
                ('liqdocumen', models.TextField(db_column='LIQDOCUMEN')),
                ('crecodigo', models.ForeignKey(db_column='CRECODIGO', on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.adtcredito')),
            ],
            options={
                'db_table': 'ADTLIQCRE',
            },
        ),
        migrations.CreateModel(
            name='Adtdetrub',
            fields=[
                ('drucodigo', models.AutoField(db_column='DRUCODIGO', primary_key=True, serialize=False)),
                ('drudescri', models.CharField(db_column='DRUDESCRI', max_length=20)),
                ('druobserv', models.CharField(blank=True, db_column='DRUOBSERV', max_length=100, null=True)),
                ('druvalor', models.DecimalField(db_column='DRUVALOR', decimal_places=2, max_digits=9)),
                ('druestado', models.CharField(db_column='DRUESTADO', max_length=3)),
                ('druusucre', models.CharField(db_column='DRUUSUCRE', max_length=15)),
                ('drufeccre', models.DateField(db_column='DRUFECCRE')),
                ('druhorcre', models.CharField(db_column='DRUHORCRE', max_length=8)),
                ('druusumod', models.CharField(blank=True, db_column='DRUUSUMOD', max_length=15, null=True)),
                ('drufecmod', models.DateField(blank=True, db_column='DRUFECMOD', null=True)),
                ('druhormod', models.CharField(blank=True, db_column='DRUHORMOD', max_length=8, null=True)),
                ('druvalotr', models.DecimalField(db_column='DRUVALOTR', decimal_places=2, max_digits=9)),
                ('drucuotas', models.CharField(db_column='DRUCUOTAS', max_length=7)),
                ('druanio', models.SmallIntegerField(db_column='DRUANIO')),
                ('drumes', models.CharField(db_column='DRUMES', max_length=2)),
                ('drusocio', models.CharField(db_column='DRUSOCIO', max_length=10)),
                ('drurubro', models.CharField(db_column='DRURUBRO', max_length=5)),
                ('rubcodigo', models.ForeignKey(db_column='RUBCODIGO', on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.adtrubros')),
            ],
            options={
                'db_table': 'ADTDETRUB',
            },
        ),
        migrations.AddField(
            model_name='adtcredito',
            name='solcodigo',
            field=models.ForeignKey(db_column='SOLCODIGO', on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.adtsolcre'),
        ),
        migrations.CreateModel(
            name='Adtclcreq',
            fields=[
                ('ccrcodigo', models.SmallAutoField(db_column='CCRCODIGO', primary_key=True, serialize=False)),
                ('ccrplamax', models.SmallIntegerField(db_column='CCRPLAMAX')),
                ('ccrtiedes', models.SmallIntegerField(db_column='CCRTIEDES')),
                ('ccrtiehas', models.SmallIntegerField(db_column='CCRTIEHAS')),
                ('ccrvalhas', models.DecimalField(db_column='CCRVALHAS', decimal_places=2, max_digits=9)),
                ('ccrestado', models.CharField(db_column='CCRESTADO', max_length=3)),
                ('ccrusucre', models.CharField(db_column='CCRUSUCRE', max_length=15)),
                ('ccrfeccre', models.DateTimeField(auto_now=True, db_column='CCRFECCRE')),
                ('ccrhorcre', models.CharField(db_column='CCRHORCRE', max_length=8)),
                ('ccrusumod', models.CharField(blank=True, db_column='CCRUSUMOD', max_length=15, null=True)),
                ('ccrfecmod', models.DateField(blank=True, db_column='CCRFECMOD', null=True)),
                ('ccrhormod', models.CharField(blank=True, db_column='CCRHORMOD', max_length=8, null=True)),
                ('clccodigo', models.ForeignKey(db_column='CLCCODIGO', on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.adtclascre')),
            ],
            options={
                'db_table': 'ADTCLCREQ',
            },
        ),
        migrations.CreateModel(
            name='Adtregdet',
            fields=[
                ('regcodigo', models.OneToOneField(db_column='REGCODIGO', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='sistema.adtregistro')),
                ('rgdcodigo', models.SmallIntegerField(db_column='RGDCODIGO')),
                ('rgdsocio', models.CharField(db_column='RGDSOCIO', max_length=10)),
                ('rgdnombre', models.CharField(db_column='RGDNOMBRE', max_length=100)),
                ('soccodigo', models.ForeignKey(db_column='SOCCODIGO', on_delete=django.db.models.deletion.DO_NOTHING, to='sistema.adtsocios')),
            ],
            options={
                'db_table': 'ADTREGDET',
                'unique_together': {('regcodigo', 'rgdcodigo')},
            },
        ),
    ]
