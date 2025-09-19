from django.db import models

# ------------------ COLABORADOR ------------------


class Colaborador(models.Model):
    rc = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Registro de Colaborador"
    )
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    sexo = models.CharField(
        max_length=10,
        choices=[("M", "Masculino"), ("F", "Feminino")]
    )
    funcao = models.CharField(max_length=50)
    cpf_rg = models.CharField(max_length=20, unique=True)
    foto = models.ImageField(upload_to="colaboradores/", blank=True, null=True)

    # Contato
    email = models.EmailField(max_length=100, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)

    # Endereço detalhado
    cep = models.CharField(max_length=10, blank=True, null=True)
    logradouro = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    bairro = models.CharField(max_length=50, blank=True, null=True)
    cidade = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    complemento = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.nome


# ------------------ INSUMO ------------------
class Insumo(models.Model):
    UNIDADES = [
        ("kg", "Kilo"),
        ("g", "Grama"),
        ("l", "Litros"),
        ("ml", "Mililitros"),
        ("un", "Unidade"),
    ]

    nome = models.CharField(max_length=100)
    quantidade = models.FloatField(
        help_text="Armazenado em unidade base (g/ml/un)"
    )
    unidade_base = models.CharField(
        max_length=10,
        choices=[("g", "Gramas"), ("ml", "Mililitros"), ("un", "Unidade")]
    )

    def __str__(self):
        return f"{self.nome} ({self.formatar_quantidade()})"

    def formatar_quantidade(self):
        """Mostra a quantidade de forma legível (ex: 1.5 kg em vez de 1500 g)."""
        if self.unidade_base == "g":
            if self.quantidade >= 1000:
                return f"{self.quantidade / 1000:.2f} kg"
            return f"{self.quantidade:.0f} g"

        elif self.unidade_base == "ml":
            if self.quantidade >= 1000:
                return f"{self.quantidade / 1000:.2f} L"
            return f"{self.quantidade:.0f} ml"

        else:  # unidade
            return f"{self.quantidade:.0f} un"


# ------------------ PRODUTO PRONTO ------------------
class ProdutoPronto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    quantidade = models.IntegerField()
    data_fabricacao = models.DateField(null=True, blank=True)
    data_validade = models.DateField(null=True, blank=True)
    # Se quiser manter preço, pode ficar
    preco = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.nome


# ------------------ SAÍDA DE INSUMO ------------------
class SaidaInsumo(models.Model):
    UNIDADES = [
        ("kg", "Quilo(s)"),
        ("g", "Grama(s)"),
        ("l", "Litro(s)"),
        ("ml", "Mililitro(s)"),
        ("un", "Unidade(s)")
    ]
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    colaborador_entregando = models.ForeignKey(
        Colaborador, on_delete=models.CASCADE, related_name='entregas'
    )
    colaborador_retira = models.ForeignKey(
        Colaborador, on_delete=models.CASCADE, related_name='retiradas'
    )
    quantidade = models.FloatField()
    unidade = models.CharField(max_length=5, choices=UNIDADES, default="un")
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantidade} {self.get_unidade_display()} de {self.insumo.nome} entregue por {self.colaborador_entregando.nome} para {self.colaborador_retira.nome}"

    def quantidade_formatada(self):
        """Converte quantidade para unidade legível usando a unidade do insumo ou da saída."""
        if self.unidade in ["g", "ml"] and self.quantidade >= 1000:
            if self.unidade == "g":
                return f"{self.quantidade / 1000:.2f} kg"
            if self.unidade == "ml":
                return f"{self.quantidade / 1000:.2f} L"
        elif self.unidade == "kg":
            return f"{self.quantidade:.2f} kg"
        elif self.unidade == "l":
            return f"{self.quantidade:.2f} L"
        elif self.unidade == "un":
            return f"{self.quantidade:.0f} un"
        return f"{self.quantidade:.0f} {self.get_unidade_display()}"
