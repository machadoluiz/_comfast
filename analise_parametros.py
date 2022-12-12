# Baixa a biblioteca SciencePlot e suas dependencias
# %%capture
!sudo apt-get install dvipng texlive-latex-extra texlive-fonts-recommended cm-super
!pip install SciencePlots

# Importa bibliotecas inerentes ao processo de analise
from google.colab import drive
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scienceplots

# Aplica modelo SciencePlots ao uso do Matplotlib para criar graficos com formatacao adequada
plt.style.use("science")

# Acessa o Google Drive
drive.mount("/gdrive", force_remount=True)

endereco_drive = "/gdrive/MyDrive/TCC/feeds.csv"

coleta_sensores_tratada = (
    pd
    # Extrai os valores do sensor do Google Drive a partir do endereco pre-definido
    .read_csv(
        endereco_drive,
        index_col="created_at",
        usecols=["created_at", "field1", "field2", "field3", "field5"],
        dtype={
            "field1": np.float64,
            "field2": np.float64,
            "field3": np.float64,
            "field5": np.float64,
        },
        parse_dates=True,
    )
    .rename(
        columns=(
            {
                "field1": "temperatura_externa",
                "field2": "umidade_externa",
                "field3": "concentracao_metano_externa",
                "field5": "temperatura_interna",
            }
        )
    )
    # Limita a valores coletados posterior ou igual a 12/11/2022 as 16h00 GMT-3
    .loc[lambda df: df.index >= "2022-11-12 16:00:00-03:00"]
    # Limita a valores coletados anterior ou igual a 11/12/2022 as 16h00 GMT-3
    .loc[lambda df: df.index <= "2022-12-11 16:00:00-03:00"]
    # Seleciona apenas valores de temperatura externa diferentes de 0.0 (erro de captura)
    .loc[lambda df: df["temperatura_externa"] != 0.0]
    # Seleciona apenas valores de temperatura externa diferentes de -127.0 (erro de captura)
    .loc[lambda df: df["temperatura_interna"] != -127.0]
    # Agrupa os valores de cada sensor sob media aritmetica diaria
    .groupby(pd.Grouper(freq="24h"))
    .mean()
    .reset_index()
)

# TEMPERATURA EXTERNA x TEMPERATURA INTERNA
temperatura_externa = coleta_sensores_tratada["temperatura_externa"]
temperatura_interna = coleta_sensores_tratada["temperatura_interna"]
tempo = coleta_sensores_tratada.index

with plt.style.context(["science", "grid"]):
    fig, ax = plt.subplots()
    ax.errorbar(tempo, temperatura_externa, yerr=2.0, fmt="-o", label="Temp. externa")
    ax.errorbar(tempo, temperatura_interna, yerr=0.5, fmt="--s", label="Temp. interna")
    ax.legend()
    ax.autoscale(tight=True)
    ax.set_xlabel("Tempo (dias)")
    ax.set_ylabel(r"Temperatura ($^{\circ}$C)")
    fig.savefig("temperaturas.jpg", dpi=300)

# TEMPERATURA INTERNA x CONCENTRACAO METANO EXTERNA
temperatura_interna = coleta_sensores_tratada["temperatura_interna"]
concentracao_metano_externa = coleta_sensores_tratada["concentracao_metano_externa"]
tempo = coleta_sensores_tratada.index

with plt.style.context(["science", "grid"]):
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.errorbar(
        tempo, temperatura_interna, yerr=0.5, fmt="--sg", label="Temp. interna"
    )
    ax2.plot(tempo, concentracao_metano_externa, "-Dy", label="Conc. CH4")
    ax1.legend(loc="upper left")
    ax2.legend(loc="lower right")
    ax1.autoscale(tight=True)
    ax1.set_xlabel("Tempo (dias)")
    ax1.set_ylabel(r"Temperatura ($^{\circ}$C)")
    ax2.set_ylabel("Concentracao (ppm)")
    fig.savefig("temperatura_concentracao_metano.jpg", dpi=300)

umidade_externa = coleta_sensores_tratada["umidade_externa"]
concentracao_metano_externa = coleta_sensores_tratada["concentracao_metano_externa"]
tempo = coleta_sensores_tratada.index

# UMIDADE EXTERNA x CONCENTRACAO METANO EXTERNA
with plt.style.context(["science", "grid"]):
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.errorbar(tempo, umidade_externa, yerr=5.0, fmt="--sb", label="Umidade Rel.")
    ax2.plot(tempo, concentracao_metano_externa, "-Dy", label="Conc. CH4")
    ax1.legend(loc="upper left")
    ax2.legend(loc="lower right")
    ax1.autoscale(tight=True)
    ax1.set_xlabel("Tempo (dias)")
    ax1.set_ylabel("Umidade Relativa (\%)")
    ax2.set_ylabel("Concentracao (ppm)")
    fig.savefig("umidade_concentracao_metano.jpg", dpi=300)
