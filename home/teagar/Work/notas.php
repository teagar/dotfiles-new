<?php
$notas = [83, 70, 87, 90  ];
$situacao = [];
$media_final = [];
$mensagem_final = "";
$notaA = 90;
$notaB = 80;
$notaC = 70;
$notaD = 60;
$notaF = 59;

function VerifyNote($notas = [0, 0]) {
  global $situacao, $notaA, $notaB, $notaC, $notaD, $notaF;
  for ($i = 0; $i < count($notas); $i++) {
    $nota = $notas[$i];
    $situacaoAtual = $situacao[$i];
    $isExcellent = $nota >= $notaB;
    $isGood = $nota >= $notaD && $nota < $notaB;
    $isBad = $nota >= 40 && $nota < $notaD;
    $isHorrible = $nota >= 0 && $nota < 40;

    if ($isExcellent) {
      $situacaoAtual = "EXCELENTE";
    } elseif ($isGood) {
      $situacaoAtual = "BOM";
    } elseif ($isBad) {
      $situacaoAtual = "RUIM";
    } elseif ($isHorrible) {
      $situacaoAtual = "PÉSSIMO";
    } else {
      $situacaoAtual = "Dado Inválido";
    }

  }

  $media_final = array_sum($notas) / count($notas);

  if ($media_final >= $notaB) {
      $situacao[$i + 1]  = "EXCELENTE";
  } elseif ($media_final >= $notaD && $media_final < $notaB) {
      $situacao[$i + 1] = "BOM";
  } elseif ($media_final >= 4 && $media_final < $notaD) {
      $situacao[$i + 1] = "RUIM";
  } elseif ($media_final >= 0 && nota < 40) {
      $situacao[$i + 1] = "PÉSSIMO";
  }
}


VerifyNote($notas);
$porcentagem_aproveitamento = ($media_final / 10) * 10;

if ($media_final >= $notaB) {
    $mensagem_final = "Parabéns! Você foi aprovado neste ano letivo situado em um nível $situacao[4] com uma porcentagem de aproveitamento de $porcentagem_aproveitamento% e uma média final de $media_final.";
} else {
    $mensagem_final = "Você precisa se esforçar mais. Sua média final foi $media_final.";
}

?>

<!DOCTYPE html>
<html>
<head>
    <title>Situação dos Bimestres</title>
</head>
<body>

<h2>Tabela de Notas e Situação por Bimestre</h2>
<table border="1">
    <tr>
        <th>1º Bimestre</th><th>Situação 1º Bimestre</th>
        <th>2º Bimestre</th><th>Situação 2º Bimestre</th>
        <th>3º Bimestre</th><th>Situação 3º Bimestre</th>
        <th>4º Bimestre</th><th>Situação 4º Bimestre</th>
    </tr>
    <tr>
        <td><?= $notas[0] ?></td><td><?= $situacao[0] ?></td>
        <td><?= $notas[1] ?></td><td><?= $situacao[1] ?></td>
        <td><?= $notas[2] ?></td><td><?= $situacao[2] ?></td>
        <td><?= $notas[3] ?></td><td><?= $situacao[3] ?></td>
    </tr>
</table>
    <br>
<table border="1">
    <tr>
        <th>Nota Exigida por Bimestre</th><th>Média Final do Aluno</th><th>Situação do Ano</th><th>Porcentagem de Aproveitamento</th>
    </tr>
    <tr>
        <td><?= $notaD?></td><td><?= $media_final ?></td><td><?= ($media_final >= $notaB) ? "EXCELENTE" : (($media_final >= $notaD) ? "BOM" : "RUIM") ?></td><td><?= $porcentagem_aproveitamento ?>%</td>
    </tr>
</table>

<h2>Mensagem Final</h2>
<p><?= $mensagem_final ?></p>

</body>
</html>
