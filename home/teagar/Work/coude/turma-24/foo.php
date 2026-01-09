<?php

function exer01() { // Apenas um teste

  $yearsOld = readline("Set your years old: ");
  $msg = "";

  if ($yearsOld > 60){ $msg = "Too old"; }
  else if ($yearsOld >= 18) { $msg = "A adult"; }
  else if ($yearsOld < 18) { $msg = "Minor person"; }
  else { $msg = "Invalid input"; }
  echo $msg;

}

function exer2() {
  $number = readline("Set your number: ");
  $msg = "";
  $isOdd = $number % 2 !== 0;

  if ($isOdd) { $msg = "Odd"; }
  else { $msg = "Even"; }

  echo $msg;
}

function exer03 () {
  $user = readline("Set your name: ");
  $pass = readline("Password: ");
  $msg = "Welcome $user";
  $logged = false;

  if ($user = "admin" && $pass = "0987") {
    $logged = true;
  }
  
  if (!$logged) {
    $msg = "you aren a user";
  }

  echo $msg;

}

function exer10() {
  $number = readline("Set a number: ");
  $msg = "$number is multiply of 3";

  if ($number % 3 != 0) {
    $msg = "$number isnt";
  }  

  echo $msg;
}

function exer11() {

  $i = 0;
  while($i <= 100) {
    if ($i % 3 != 0) {
      $msg = "$i isnt";
    }  else {
      $msg = "$i is multiply of 3";
    }
    echo $msg."\n";
    $i++;
  }


}

exer11();
