from django import forms
from .models import Colaborador, Insumo, ProdutoPronto, SaidaInsumo

# ---------- FORMULÁRIO DE COLABORADOR ----------


class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = [
            'rc', 'nome', 'data_nascimento',
            'cep', 'logradouro', 'numero', 'bairro', 'cidade', 'estado', 'complemento',
            'funcao', 'sexo', 'cpf_rg', 'celular', 'email', 'foto'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'funcao': forms.TextInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'logradouro': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'rc': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_rg': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(99) 99999-9999'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

# ---------- FORMULÁRIO DE INSUMO ----------


class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ["nome", "quantidade", "unidade_base"]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'unidade_base': forms.Select(attrs={'class': 'form-select'}),
        }

# ---------- FORMULÁRIO DE PRODUTO PRONTO ----------


class ProdutoProntoForm(forms.ModelForm):
    class Meta:
        model = ProdutoPronto
        # removemos 'preco'
        fields = ['nome', 'descricao', 'quantidade',
                  'data_fabricacao', 'data_validade']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'data_fabricacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_validade': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

# ---------- FORMULÁRIO DE SAÍDA DE INSUMO ----------


class SaidaInsumoForm(forms.ModelForm):
    UNIDADES_CONVERSAO = {
        'kg': 1000,   # 1 kg = 1000 g
        'g': 1,
        'l': 1000,    # 1 L = 1000 ml
        'ml': 1,
        'un': 1
    }

    class Meta:
        model = SaidaInsumo
        fields = ['insumo', 'colaborador_entregando',
                  'colaborador_retira', 'quantidade', 'unidade']
        widgets = {
            'insumo': forms.Select(attrs={'class': 'form-select'}),
            'colaborador_entregando': forms.Select(attrs={'class': 'form-select'}),
            'colaborador_retira': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 0.01, 'step': '0.01'}),
            'unidade': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['insumo'].queryset = Insumo.objects.filter(
            quantidade__gt=0)
        self.fields['colaborador_entregando'].queryset = Colaborador.objects.all()
        self.fields['colaborador_retira'].queryset = Colaborador.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        quantidade = cleaned_data.get('quantidade')
        unidade = cleaned_data.get('unidade')
        insumo = cleaned_data.get('insumo')

        if quantidade and unidade and insumo:
            fator = self.UNIDADES_CONVERSAO[unidade] / \
                self.UNIDADES_CONVERSAO[insumo.unidade_base]
            quantidade_base = quantidade * fator

            if quantidade_base > insumo.quantidade:
                raise forms.ValidationError(
                    f"A quantidade solicitada ({quantidade} {unidade}) excede o estoque disponível "
                    f"({insumo.quantidade} {insumo.unidade_base}) de {insumo.nome}."
                )

            cleaned_data['quantidade'] = quantidade_base

        return cleaned_data
