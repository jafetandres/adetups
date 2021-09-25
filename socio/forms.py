from django import forms

from sistema.models import SolicitudCredito, Socio, Credito



class SolicitudCreditoForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     user=requ
    #     self.user = kwargs.pop('user', None)
    #     print(self.user)
    #     super(SolicitudCreditoForm, self).__init__(*args, **kwargs)

    def clean_monto(self):
        clasecredito = self.cleaned_data['clasecredito']
        monto = self.cleaned_data['monto']

        # if monto > clasecredito.valhasta:
        #     raise forms.ValidationError("El monto excede a la clase de credito")
        # if monto < clasecredito.valdesde:
        #     raise forms.ValidationError("El monto esta por de bajo del limite a la clase de credito")
        return monto

    def clean_plazo(self):
        clasecredito = self.cleaned_data['clasecredito']
        plazo = self.cleaned_data['plazo']
        # if plazo > clasecredito.plazomax:
        #     raise forms.ValidationError("El plazo excede a la clase de credito")
        # if plazo < 1:
        #     raise forms.ValidationError("El plazo debe ser mayor a 1 mes")
        return plazo

    # def clean(self):
    #     if Credito.objects.filter(socio=socio).exists():
    #         raise forms.ValidationError('El socio ya tiene un prestamo activo y no puede solicitar otro')

    class Meta:
        model = SolicitudCredito
        fields = ['clasecredito', 'garante', 'monto', 'plazo']
