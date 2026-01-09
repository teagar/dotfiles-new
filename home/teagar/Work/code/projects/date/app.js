const fs = require('fs');
const moment = require('moment');

function addCurrentTimeToFile() {
  // Obter o horário atual
  const current_time = moment().format('YYYY-MM-DD HH:mm:ss');

  // Adicionar o horário atual em uma nova linha no arquivo hour.txt
  fs.appendFile('hour.txt', current_time + '\n', (err) => {
    if (err) {
      console.error('Ocorreu um erro ao escrever no arquivo:', err);
    } else {
      console.log('Horário adicionado ao arquivo com sucesso!');
    }
  });
}

// Chamar a função inicialmente e, em seguida, a cada 1 minuto
addCurrentTimeToFile();
setInterval(addCurrentTimeToFile, 60000); // 60000 milissegundos = 1 minuto

