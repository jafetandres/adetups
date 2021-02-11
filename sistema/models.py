from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class PersonalizadoBaseUserManager(BaseUserManager):
    def create_user(self, username, password):
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password)
        user.is_staff = True
        user.is_superuser = True
        user.tipo = 'administrador'
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser, PermissionsMixin):
    foto = models.ImageField(upload_to='img_perfil', null=True, blank=True, default='img_perfil/default-avatar.jpg')
    nombres = models.CharField(max_length=50, null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now, null=True, blank=True)
    apellidos = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=50, null=True, blank=True, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    is_staff = models.BooleanField(default=False, null=True, blank=True)
    tipo = models.CharField(max_length=20, null=True, blank=True)
    USERNAME_FIELD = 'username'
    objects = PersonalizadoBaseUserManager()

    def get_full_name(self):
        return self.nombres, self.apellidos

    def get_short_name(self):
        return self.nombres


class Rubro(models.Model):
    descripcion = models.CharField(max_length=50, null=True, blank=True)
    tipo = models.CharField(max_length=10, null=True, blank=True)
    estado = models.BooleanField(default=True, null=True, blank=True)
    valor = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    abreviatura = models.CharField(max_length=10, null=True, blank=True, unique=True)

    def __str__(self):
        return self.descripcion


class RubroSocio(models.Model):
    rubro = models.ForeignKey(Rubro, models.DO_NOTHING)  # Field name made lowercase.
    descripcion = models.CharField(max_length=20, blank=True, null=True)  # Field name made lowercase.
    servicio = models.CharField(max_length=100, blank=True,
                                null=True)  # Field name made lowercase.
    valor = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    estado = models.CharField(max_length=3, blank=True, null=True)  # Field name made lowercase.
    fecha_ingreso = models.DateField(auto_now=True, blank=True, null=True)  # Field name made lowercase.

    # druvalotr = models.DecimalField(max_digits=9, decimal_places=2)  # Field name made lowercase.
    cuotas = models.CharField(max_length=7, blank=True, null=True)  # Field name made lowercase.

    def __str__(self):
        return self.descripcion


class Socio(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    # cedula = models.CharField(unique=True, max_length=10)  # Field name made lowercase.
    direccion = models.CharField(max_length=80, null=True, blank=True)  # Field name made lowercase.
    telefono = models.CharField(max_length=15, null=True, blank=True)  # Field name made lowercase.
    celular = models.CharField(max_length=10, null=True, blank=True)  # Field name made lowercase.
    cargo = models.CharField(max_length=20, null=True, blank=True)  # Field name made lowercase.
    area = models.CharField(max_length=20, null=True, blank=True)  # Field name made lowercase.
    fecha_ingreso = models.DateField(blank=True, null=True)  # Field name made lowercase.
    is_garante = models.BooleanField(default=False, null=True, blank=True)
    rubros = models.ManyToManyField(RubroSocio, blank=True, null=True)
    # tiempo = models.SmallIntegerField()  # Field name made lowercase.


class Adtclascre(models.Model):
    clccodigo = models.SmallAutoField(db_column='CLCCODIGO', primary_key=True)  # Field name made lowercase.
    clcdescri = models.CharField(db_column='CLCDESCRI', max_length=30)  # Field name made lowercase.
    clcvaldes = models.DecimalField(db_column='CLCVALDES', max_digits=6, decimal_places=2)  # Field name made lowercase.
    clcvalhas = models.DecimalField(db_column='CLCVALHAS', max_digits=6, decimal_places=2)  # Field name made lowercase.
    clcautori = models.CharField(db_column='CLCAUTORI', max_length=2)  # Field name made lowercase.
    clcestado = models.CharField(db_column='CLCESTADO', max_length=3)  # Field name made lowercase.
    clcusucre = models.CharField(db_column='CLCUSUCRE', max_length=15)  # Field name made lowercase.
    clcfeccre = models.DateTimeField(db_column='CLCFECCRE', auto_now=True)  # Field name made lowercase.
    clchorcre = models.CharField(db_column='CLCHORCRE', max_length=8)  # Field name made lowercase.
    clcusumod = models.CharField(db_column='CLCUSUMOD', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    clcfecmod = models.DateField(db_column='CLCFECMOD', blank=True, null=True)  # Field name made lowercase.
    clchormod = models.CharField(db_column='CLCHORMOD', max_length=8, blank=True,
                                 null=True)  # Field name made lowercase.
    clcplamax = models.SmallIntegerField(db_column='CLCPLAMAX')  # Field name made lowercase.
    clcgarant = models.CharField(db_column='CLCGARANT', max_length=2)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTCLASCRE'

    def __str__(self):
        return self.clcdescri


class ClaseCredito(models.Model):
    descripcion = models.CharField(max_length=30, blank=True, null=True)
    valdesde = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    valhasta = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    autorizacion = models.BooleanField(default=True, blank=True, null=True)  # Field name made lowercase.
    estado = models.CharField(max_length=10, blank=True, null=True)  # Field name made lowercase.
    plazomax = models.SmallIntegerField(blank=True, null=True)  # Field name made lowercase.
    porcentaje_interes = models.DecimalField(max_digits=4, decimal_places=2, blank=True,
                                             null=True)  # Field name made lowercase.
    tiempo_minimo_servicio = models.IntegerField(blank=True, null=True)
    garante = models.BooleanField(default=True, blank=True, null=True)  # Field name made lowercase.
    # parametros = models.ManyToManyField(Parametro, blank=True, null=True)


class RestriccionClaseCredito(models.Model):
    clasecredito = models.ForeignKey(ClaseCredito, models.DO_NOTHING)
    tiempo_desde = models.SmallIntegerField(blank=True,
                                            null=True)  # Field name made lowercase.
    tiempo_hasta = models.SmallIntegerField(blank=True,
                                            null=True)  # Field name made lowercase.
    valhasta = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    estado = models.BooleanField(default=True, blank=True, null=True)  # Field name made lowercase.
    fecha_creacion = models.DateTimeField(auto_now=True, blank=True, null=True)


class Parametro(models.Model):
    clasecredito = models.ForeignKey(ClaseCredito, models.CASCADE)
    descripcion = models.CharField(max_length=100)  # Field name made lowercase.
    valorcaracter = models.CharField(max_length=200)  # Field name made lowercase.
    valornumerico = models.DecimalField(max_digits=9, decimal_places=2)  # Field name made lowercase.
    estado = models.BooleanField(default=False)  # Field name made lowercase.


class Adtclasol(models.Model):
    csocodigo = models.SmallAutoField(db_column='CSOCODIGO', primary_key=True)  # Field name made lowercase.
    csoabrev = models.CharField(db_column='CSOABREV', unique=True, max_length=5)  # Field name made lowercase.
    csodescri = models.CharField(db_column='CSODESCRI', max_length=30)  # Field name made lowercase.
    csoestado = models.CharField(db_column='CSOESTADO', max_length=3)  # Field name made lowercase.
    csousucre = models.CharField(db_column='CSOUSUCRE', max_length=15)  # Field name made lowercase.
    csofeccre = models.DateTimeField(auto_now=True, db_column='CSOFECCRE')  # Field name made lowercase.
    csohorcre = models.CharField(db_column='CSOHORCRE', max_length=8)  # Field name made lowercase.
    csousumod = models.CharField(db_column='CSOUSUMOD', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    csofecmod = models.DateField(db_column='CSOFECMOD', blank=True, null=True)  # Field name made lowercase.
    csohormod = models.CharField(db_column='CSOHORMOD', max_length=8, blank=True,
                                 null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTCLASOL'


# class ClaseSolicitud(models.Model):
#     descripcion = models.CharField(max_length=30)  # Field name made lowercase.
#     estado = models.CharField(max_length=10)  # Field name made lowercase.


class SolicitudCredito(models.Model):
    clasecredito = models.ForeignKey(ClaseCredito, models.CASCADE, blank=True, null=True)
    fecha_ingreso = models.DateTimeField(auto_now=True)
    garante = models.ForeignKey(Socio, models.DO_NOTHING, related_name='garante')
    monto = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    plazo = models.SmallIntegerField(blank=True, null=True)
    estado = models.CharField(max_length=20, default='pendiente', blank=True, null=True)
    socio = models.ForeignKey(Socio, models.DO_NOTHING, related_name='socio', blank=True, null=True)
    # cuota = models.DecimalField(max_digits=9, decimal_places=2)
    # interes = models.DecimalField(max_digits=9, decimal_places=2)
    porcentaje_interes = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)


class Adtclcreq(models.Model):
    ccrcodigo = models.SmallAutoField(db_column='CCRCODIGO', primary_key=True)  # Field name made lowercase.
    clccodigo = models.ForeignKey(Adtclascre, on_delete=models.DO_NOTHING, db_column='CLCCODIGO',
                                  )  # Field name made lowercase.
    ccrplamax = models.SmallIntegerField(db_column='CCRPLAMAX')  # Field name made lowercase.
    ccrtiedes = models.SmallIntegerField(db_column='CCRTIEDES')  # Field name made lowercase.
    ccrtiehas = models.SmallIntegerField(db_column='CCRTIEHAS')  # Field name made lowercase.
    ccrvalhas = models.DecimalField(db_column='CCRVALHAS', max_digits=9, decimal_places=2)  # Field name made lowercase.
    ccrestado = models.CharField(db_column='CCRESTADO', max_length=3)  # Field name made lowercase.
    ccrusucre = models.CharField(db_column='CCRUSUCRE', max_length=15)  # Field name made lowercase.
    ccrfeccre = models.DateTimeField(auto_now=True, db_column='CCRFECCRE')  # Field name made lowercase.
    ccrhorcre = models.CharField(db_column='CCRHORCRE', max_length=8)  # Field name made lowercase.
    ccrusumod = models.CharField(db_column='CCRUSUMOD', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    ccrfecmod = models.DateField(db_column='CCRFECMOD', blank=True, null=True)  # Field name made lowercase.
    ccrhormod = models.CharField(db_column='CCRHORMOD', max_length=8, blank=True,
                                 null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTCLCREQ'


class Adtcredito(models.Model):
    crecodigo = models.BigAutoField(db_column='CRECODIGO', primary_key=True)  # Field name made lowercase.
    solcodigo = models.ForeignKey('Adtsolcre', models.DO_NOTHING, db_column='SOLCODIGO')  # Field name made lowercase.
    cresocio = models.CharField(db_column='CRESOCIO', max_length=10)  # Field name made lowercase.
    cremonto = models.DecimalField(db_column='CREMONTO', max_digits=9, decimal_places=2)  # Field name made lowercase.
    crecuota = models.DecimalField(db_column='CRECUOTA', max_digits=9, decimal_places=2)  # Field name made lowercase.
    creintere = models.DecimalField(db_column='CREINTERE', max_digits=4, decimal_places=2)  # Field name made lowercase.
    creplazo = models.SmallIntegerField(db_column='CREPLAZO')  # Field name made lowercase.
    crenrocob = models.SmallIntegerField(db_column='CRENROCOB')  # Field name made lowercase.
    crepagado = models.DecimalField(db_column='CREPAGADO', max_digits=9, decimal_places=2)  # Field name made lowercase.
    creestado = models.CharField(db_column='CREESTADO', max_length=3)  # Field name made lowercase.
    creusucre = models.CharField(db_column='CREUSUCRE', max_length=15)  # Field name made lowercase.
    crehorcre = models.CharField(db_column='CREHORCRE', max_length=8)  # Field name made lowercase.
    crefeccre = models.DateField(db_column='CREFECCRE')  # Field name made lowercase.
    creusumod = models.CharField(db_column='CREUSUMOD', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    crefecmod = models.DateField(db_column='CREFECMOD', blank=True, null=True)  # Field name made lowercase.
    crehormod = models.CharField(db_column='CREHORMOD', max_length=8, blank=True,
                                 null=True)  # Field name made lowercase.
    crependien = models.DecimalField(db_column='CREPENDIEN', max_digits=9,
                                     decimal_places=2)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTCREDITO'


class Cuota(models.Model):
    estado = models.BooleanField(default=False, null=True, blank=True)
    capital = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    interes = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    saldo_capital = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    orden = models.SmallIntegerField()
    fecha_pago = models.DateField()
    valor_cuota = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)


class Credito(models.Model):
    solicitud = models.ForeignKey(SolicitudCredito, models.DO_NOTHING)  # Field name made lowercase.
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, db_constraint=False)  # Field name made lowercase.
    monto = models.DecimalField(max_digits=9, decimal_places=2)  # Field name made lowercase.
    cuotas = models.ManyToManyField(Cuota)
    porcentaje_interes = models.DecimalField(max_digits=4, decimal_places=2)  # Field name made lowercase.
    fecha_ingreso = models.DateField(auto_now=True)
    plazo = models.SmallIntegerField()  # Field name made lowercase.
    # crenrocob = models.SmallIntegerField()  # Field name made lowercase.
    # pagado = models.DecimalField(max_digits=9, decimal_places=2)  # Field name made lowercase.
    estado = models.CharField(max_length=3)  # Field name made lowercase.
    # pendiente = models.DecimalField(db_column='CREPENDIEN', max_digits=9,
    #                                 decimal_places=2)  # Field name made lowercase.


class Adtdetrub(models.Model):
    drucodigo = models.AutoField(db_column='DRUCODIGO', primary_key=True)  # Field name made lowercase.
    rubcodigo = models.ForeignKey('Adtrubros', models.DO_NOTHING, db_column='RUBCODIGO')  # Field name made lowercase.
    drudescri = models.CharField(db_column='DRUDESCRI', max_length=20)  # Field name made lowercase.
    druobserv = models.CharField(db_column='DRUOBSERV', max_length=100, blank=True,
                                 null=True)  # Field name made lowercase.
    druvalor = models.DecimalField(db_column='DRUVALOR', max_digits=9, decimal_places=2)  # Field name made lowercase.
    druestado = models.CharField(db_column='DRUESTADO', max_length=3)  # Field name made lowercase.
    druusucre = models.CharField(db_column='DRUUSUCRE', max_length=15)  # Field name made lowercase.
    drufeccre = models.DateField(db_column='DRUFECCRE')  # Field name made lowercase.
    druhorcre = models.CharField(db_column='DRUHORCRE', max_length=8)  # Field name made lowercase.
    druusumod = models.CharField(db_column='DRUUSUMOD', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    drufecmod = models.DateField(db_column='DRUFECMOD', blank=True, null=True)  # Field name made lowercase.
    druhormod = models.CharField(db_column='DRUHORMOD', max_length=8, blank=True,
                                 null=True)  # Field name made lowercase.
    druvalotr = models.DecimalField(db_column='DRUVALOTR', max_digits=9, decimal_places=2)  # Field name made lowercase.
    drucuotas = models.CharField(db_column='DRUCUOTAS', max_length=7)  # Field name made lowercase.
    druanio = models.SmallIntegerField(db_column='DRUANIO')  # Field name made lowercase.
    drumes = models.CharField(db_column='DRUMES', max_length=2)  # Field name made lowercase.
    drusocio = models.CharField(db_column='DRUSOCIO', max_length=10)  # Field name made lowercase.
    drurubro = models.CharField(db_column='DRURUBRO', max_length=5)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTDETRUB'


class Adtliqcre(models.Model):
    liqcodigo = models.AutoField(db_column='LIQCODIGO', primary_key=True)  # Field name made lowercase.
    crecodigo = models.ForeignKey(Adtcredito, models.DO_NOTHING, db_column='CRECODIGO')  # Field name made lowercase.
    liqvalor = models.DecimalField(db_column='LIQVALOR', max_digits=9, decimal_places=2)  # Field name made lowercase.
    liqobserv = models.CharField(db_column='LIQOBSERV', max_length=200)  # Field name made lowercase.
    liqestado = models.CharField(db_column='LIQESTADO', max_length=3)  # Field name made lowercase.
    liqusucre = models.CharField(db_column='LIQUSUCRE', max_length=15)  # Field name made lowercase.
    liqfeccre = models.DateField(db_column='LIQFECCRE')  # Field name made lowercase.
    liqhorcre = models.CharField(db_column='LIQHORCRE', max_length=10)  # Field name made lowercase.
    liqdocumen = models.TextField(db_column='LIQDOCUMEN')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTLIQCRE'


class LiquidacionCredito(models.Model):
    credito = models.ForeignKey(Credito, models.DO_NOTHING)  # Field name made lowercase.
    valor = models.DecimalField(max_digits=9, decimal_places=2)  # Field name made lowercase.
    observacion = models.CharField(max_length=200)  # Field name made lowercase.
    documento = models.TextField(null=True, blank=True)  # Field name made lowercase.


# class Adtlogsol(models.Model):
#     lsocodigo = models.BigAutoField(db_column='LSOCODIGO', primary_key=True)  # Field name made lowercase.
#     lsocodsol = models.BigIntegerField(db_column='LSOCODSOL')  # Field name made lowercase.
#     lsocsocod = models.SmallIntegerField(db_column='LSOCSOCOD')  # Field name made lowercase.
#     lsoestado = models.CharField(db_column='LSOESTADO', max_length=3)  # Field name made lowercase.
#     lsoobserv = models.CharField(db_column='LSOOBSERV', max_length=254)  # Field name made lowercase.
#     lsousucre = models.CharField(db_column='LSOUSUCRE', max_length=15)  # Field name made lowercase.
#     lsofeccre = models.DateField(db_column='LSOFECCRE')  # Field name made lowercase.
#     lsohorcre = models.CharField(db_column='LSOHORCRE', max_length=8)  # Field name made lowercase.
#
#     class Meta:
#         # managed = False
#         db_table = 'ADTLOGSOL'
#


class Adtparam(models.Model):
    prmcodigo = models.CharField(db_column='PRMCODIGO', primary_key=True, max_length=10)  # Field name made lowercase.
    prmdescri = models.CharField(db_column='PRMDESCRI', max_length=100)  # Field name made lowercase.
    prmcarac = models.CharField(db_column='PRMCARAC', max_length=200)  # Field name made lowercase.
    prmnumer = models.DecimalField(db_column='PRMNUMER', max_digits=9, decimal_places=2)  # Field name made lowercase.
    prmfecha = models.DateField(db_column='PRMFECHA')  # Field name made lowercase.
    prmusucre = models.CharField(db_column='PRMUSUCRE', max_length=15)  # Field name made lowercase.
    prmfeccre = models.DateField(db_column='PRMFECCRE')  # Field name made lowercase.
    prmhorcre = models.CharField(db_column='PRMHORCRE', max_length=8)  # Field name made lowercase.
    prmusumod = models.CharField(db_column='PRMUSUMOD', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    prmfecmod = models.DateField(db_column='PRMFECMOD', blank=True, null=True)  # Field name made lowercase.
    prmhormod = models.CharField(db_column='PRMHORMOD', max_length=8, blank=True,
                                 null=True)  # Field name made lowercase.
    prmestado = models.CharField(db_column='PRMESTADO', max_length=3)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTPARAM'


class Adtperfil(models.Model):
    percodigo = models.CharField(db_column='PERCODIGO', primary_key=True, max_length=10)  # Field name made lowercase.
    perdescri = models.CharField(db_column='PERDESCRI', max_length=25)  # Field name made lowercase.
    perestado = models.CharField(db_column='PERESTADO', max_length=3)  # Field name made lowercase.
    perusucre = models.CharField(db_column='PERUSUCRE', max_length=15)  # Field name made lowercase.
    perfeccre = models.DateField(db_column='PERFECCRE', null=True, blank=True)  # Field name made lowercase.
    perhorcre = models.CharField(db_column='PERHORCRE', max_length=8, null=True,
                                 blank=True)  # Field name made lowercase.
    perusumod = models.CharField(db_column='PERUSUMOD', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    perfecmod = models.DateField(db_column='PERFECMOD', blank=True, null=True)  # Field name made lowercase.
    perhormod = models.CharField(db_column='PERHORMOD', max_length=8, blank=True,
                                 null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTPERFIL'


class Adtregdet(models.Model):
    regcodigo = models.OneToOneField('Adtregistro', models.DO_NOTHING, db_column='REGCODIGO',
                                     primary_key=True)  # Field name made lowercase.
    rgdcodigo = models.SmallIntegerField(db_column='RGDCODIGO')  # Field name made lowercase.
    rgdsocio = models.CharField(db_column='RGDSOCIO', max_length=10)  # Field name made lowercase.
    rgdnombre = models.CharField(db_column='RGDNOMBRE', max_length=100)  # Field name made lowercase.
    soccodigo = models.ForeignKey('Adtsocios', models.DO_NOTHING, db_column='SOCCODIGO')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTREGDET'
        unique_together = (('regcodigo', 'rgdcodigo'),)


class Adtregistro(models.Model):
    regcodigo = models.AutoField(db_column='REGCODIGO', primary_key=True)  # Field name made lowercase.
    regnombre = models.CharField(db_column='REGNOMBRE', max_length=20)  # Field name made lowercase.
    regcedrep = models.CharField(db_column='REGCEDREP', max_length=10)  # Field name made lowercase.
    regnomrep = models.CharField(db_column='REGNOMREP', max_length=100)  # Field name made lowercase.
    regfeccre = models.DateField(db_column='REGFECCRE')  # Field name made lowercase.
    reghorcre = models.CharField(db_column='REGHORCRE', max_length=8)  # Field name made lowercase.
    regcatego = models.SmallIntegerField(db_column='REGCATEGO')  # Field name made lowercase.
    regusucre = models.CharField(db_column='REGUSUCRE', max_length=15)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTREGISTRO'


class Adtrubros(models.Model):
    rubcodigo = models.SmallAutoField(db_column='RUBCODIGO', primary_key=True)  # Field name made lowercase.
    rubabrev = models.CharField(db_column='RUBABREV', unique=True, max_length=5)  # Field name made lowercase.
    rubdescri = models.CharField(db_column='RUBDESCRI', max_length=50)  # Field name made lowercase.
    rubtipo = models.CharField(db_column='RUBTIPO', max_length=3)  # Field name made lowercase.
    rubestado = models.CharField(db_column='RUBESTADO', max_length=3)  # Field name made lowercase.
    rubusucre = models.CharField(db_column='RUBUSUCRE', max_length=15)  # Field name made lowercase.
    rubfeccre = models.DateField(db_column='RUBFECCRE')  # Field name made lowercase.
    rubhorcre = models.CharField(db_column='RUBHORCRE', max_length=8)  # Field name made lowercase.
    rubusumod = models.CharField(db_column='RUBUSUMOD', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    rubfecmod = models.DateField(db_column='RUBFECMOD', blank=True, null=True)  # Field name made lowercase.
    rubhormod = models.CharField(db_column='RUBHORMOD', max_length=8, blank=True,
                                 null=True)  # Field name made lowercase.
    rubvalor = models.DecimalField(db_column='RUBVALOR', max_digits=9, decimal_places=2)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTRUBROS'


class Adtrubsoc(models.Model):
    rsocodigo = models.BigAutoField(db_column='RSOCODIGO', primary_key=True)  # Field name made lowercase.
    rsosocio = models.CharField(db_column='RSOSOCIO', max_length=10)  # Field name made lowercase.
    rsoanio = models.SmallIntegerField(db_column='RSOANIO')  # Field name made lowercase.
    rsomes = models.CharField(db_column='RSOMES', max_length=2)  # Field name made lowercase.
    rsovalor = models.DecimalField(db_column='RSOVALOR', max_digits=9, decimal_places=2)  # Field name made lowercase.
    rubcodigo = models.ForeignKey(Adtrubros, models.DO_NOTHING, db_column='RUBCODIGO')  # Field name made lowercase.
    rsorubro = models.CharField(db_column='RSORUBRO', max_length=5)  # Field name made lowercase.
    rsoestado = models.CharField(db_column='RSOESTADO', max_length=3)  # Field name made lowercase.
    rsofeccre = models.DateField(db_column='RSOFECCRE')  # Field name made lowercase.
    rsohorcre = models.CharField(db_column='RSOHORCRE', max_length=8)  # Field name made lowercase.
    rsousucre = models.CharField(db_column='RSOUSUCRE', max_length=15)  # Field name made lowercase.
    rsorefere = models.CharField(db_column='RSOREFERE', max_length=10, blank=True,
                                 null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTRUBSOC'


#
# class RubroSocio(models.Model):
#     socio = models.CharField(Socio, max_length=10)  # Field name made lowercase.
#     fecha = models.DateTimeField(auto_now=True)
#     valor = models.DecimalField(db_column='RSOVALOR', max_digits=9, decimal_places=2)  # Field name made lowercase.
#     rubro = models.ForeignKey(Rubro, models.DO_NOTHING, db_column='RUBCODIGO')  # Field name made lowercase.
#     estado = models.CharField(db_column='RSOESTADO', max_length=3)  # Field name made lowercase.
#

class Adtsocios(models.Model):
    soccodigo = models.AutoField(db_column='SOCCODIGO', primary_key=True)  # Field name made lowercase.
    soccedula = models.CharField(db_column='SOCCEDULA', unique=True, max_length=10)  # Field name made lowercase.
    socnombre = models.CharField(db_column='SOCNOMBRE', max_length=50)  # Field name made lowercase.
    socapelli = models.CharField(db_column='SOCAPELLI', max_length=50)  # Field name made lowercase.
    socdirecc = models.CharField(db_column='SOCDIRECC', max_length=80)  # Field name made lowercase.
    soctelefe = models.CharField(db_column='SOCTELEFE', max_length=15)  # Field name made lowercase.
    socmovil = models.CharField(db_column='SOCMOVIL', max_length=10)  # Field name made lowercase.
    socemail = models.CharField(db_column='SOCEMAIL', max_length=100)  # Field name made lowercase.
    soccargo = models.CharField(db_column='SOCCARGO', max_length=20)  # Field name made lowercase.
    socestado = models.CharField(db_column='SOCESTADO', max_length=3)  # Field name made lowercase.
    socusucre = models.CharField(null=True, blank=True, db_column='SOCUSUCRE',
                                 max_length=15)  # Field name made lowercase.
    socfeccre = models.DateField(db_column='SOCFECCRE')  # Field name made lowercase.
    sochorcre = models.CharField(db_column='SOCHORCRE', max_length=8)  # Field name made lowercase.
    socusumod = models.CharField(db_column='SOCUSUMOD', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    socfecmod = models.DateField(db_column='SOCFECMOD', blank=True, null=True)  # Field name made lowercase.
    sochormod = models.CharField(db_column='SOCHORMOD', max_length=8, blank=True,
                                 null=True)  # Field name made lowercase.
    socarea = models.CharField(db_column='SOCAREA', max_length=20)  # Field name made lowercase.
    socfecing = models.DateField(db_column='SOCFECING', blank=True, null=True)  # Field name made lowercase.
    soctiempo = models.SmallIntegerField(db_column='SOCTIEMPO')  # Field name made lowercase.
    socfoto = models.TextField(db_column='SOCFOTO')  # Field name made lowercase.
    socgenero = models.CharField(db_column='SOCGENERO', max_length=10)  # Field name made lowercase.
    soctipo = models.CharField(db_column='SOCTIPO', max_length=5)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTSOCIOS'


class Adtsolcre(models.Model):
    solcodigo = models.BigAutoField(db_column='SOLCODIGO', primary_key=True)  # Field name made lowercase.
    clccodigo = models.ForeignKey(Adtclascre, models.DO_NOTHING, db_column='CLCCODIGO')  # Field name made lowercase.
    solfeccre = models.DateTimeField(auto_now=True, db_column='SOLFECCRE')  # Field name made lowercase.
    solcedgar = models.CharField(db_column='SOLCEDGAR', max_length=10)  # Field name made lowercase.
    solmonto = models.DecimalField(db_column='SOLMONTO', max_digits=9, decimal_places=2)  # Field name made lowercase.
    solplazo = models.SmallIntegerField(db_column='SOLPLAZO')  # Field name made lowercase.
    solestado = models.CharField(db_column='SOLESTADO', max_length=10, default='tramite')  # Field name made lowercase.
    csocodigo = models.ForeignKey(Adtclasol, models.DO_NOTHING, db_column='CSOCODIGO')  # Field name made lowercase.
    soccodigo = models.ForeignKey(Adtsocios, models.DO_NOTHING, db_column='SOCCODIGO')  # Field name made lowercase.
    solcuota = models.DecimalField(db_column='SOLCUOTA', max_digits=9, decimal_places=2)  # Field name made lowercase.
    solintere = models.DecimalField(db_column='SOLINTERE', max_digits=9, decimal_places=2)  # Field name made lowercase.
    solporint = models.DecimalField(db_column='SOLPORINT', max_digits=4, decimal_places=2)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTSOLCRE'


class Adtusuario(models.Model):
    usucodigo = models.AutoField(db_column='USUCODIGO', primary_key=True)  # Field name made lowercase.
    usuclave = models.CharField(db_column='USUCLAVE', max_length=80)  # Field name made lowercase.
    percodigo = models.ForeignKey(Adtperfil, models.DO_NOTHING, db_column='PERCODIGO')  # Field name made lowercase.
    usuestado = models.CharField(db_column='USUESTADO', max_length=3)  # Field name made lowercase.
    usuusucre = models.CharField(db_column='USUUSUCRE', max_length=15)  # Field name made lowercase.
    usufeccre = models.DateField(db_column='USUFECCRE')  # Field name made lowercase.
    usuhorcre = models.CharField(db_column='USUHORCRE', max_length=8)  # Field name made lowercase.
    usuusumod = models.CharField(db_column='USUUSUMOD', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    usufecmod = models.DateField(db_column='USUFECMOD', blank=True, null=True)  # Field name made lowercase.
    usuhormod = models.CharField(db_column='USUHORMOD', max_length=8, blank=True,
                                 null=True)  # Field name made lowercase.
    soccodigo = models.ForeignKey(Adtsocios, models.DO_NOTHING, db_column='SOCCODIGO')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ADTUSUARIO'
