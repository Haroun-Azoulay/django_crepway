// fonction pop up
function closeModale() {
  $('#myModal').modal('hide');
}
$(document).ready(function() {
  $('#myModal').on('hidden.bs.modal', function () {
    $('#myModal').remove(); // Supprime complètement la fenêtre modale du DOM
  });
  $('#myModal').modal('show');
});

// Fonction pour définir un cookie
function setCookie(name, value, days) {
  const date = new Date();
  date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
  const expires = "expires=" + date.toUTCString();
  const sameSite = "SameSite=None; Secure"; // Ajouter les attributs SameSite=None et Secure
  document.cookie = name + "=" + value + ";" + expires + ";path=/;" + sameSite;
}

// Fonction pour récupérer la valeur d'un cookie
function getCookie(name) {
  const cookieName = name + "=";
  const cookieArray = document.cookie.split(";");
  for (let i = 0; i < cookieArray.length; i++) {
    let cookie = cookieArray[i];
    while (cookie.charAt(0) === " ") {
      cookie = cookie.substring(1);
    }
    if (cookie.indexOf(cookieName) === 0) {
      return cookie.substring(cookieName.length, cookie.length);
    }
  }
  return "";
}

// Appel de la fonction au chargement de la page pour restaurer la sélection
window.addEventListener('load', function() {
  const savedOption = getCookie('selectedOption');
  const savedLocation = getCookie('selectedLocation');
  displayField(savedOption, savedLocation);
});

function displayField(typeChamp, location) {
  const champContainer = document.getElementById('champContainer');
  const selectedLocation = document.getElementById('selectedLocation');
  const buttonValidateOrder = document.getElementById('buttonValidateOrder');
  champContainer.innerHTML = ''; // Effacer le contenu précédent

  if (typeChamp === 'take away' || typeChamp === 'in place') {
    const champTexte = document.createElement('input');
    champTexte.type = 'text';
    champTexte.name = 'adresse';
    champTexte.readOnly = true;
    champTexte.value = '130 Route de Mitry, Aulnay-sous-Bois';
    champTexte.style.width = '300px';
    champContainer.appendChild(champTexte);
    buttonValidateOrder.classList.remove('d-none');
    selectedLocation.textContent = 'À retirer dans 30 min au restaurant:  130 Route de Mitry, 93600 Aulnay-sous-Bois';
    selectedLocation.style.color = 'white';

    // Sauvegarder la sélection dans un cookie
    setCookie('selectedOption', typeChamp, 7); // Le cookie expire après 7 jours
    setCookie('selectedLocation', '', 7); // Effacer la valeur du cookie de l'emplacement
  } else if (typeChamp === 'delivery') {
    const select = document.createElement('select');
    select.name = 'ville';
    select.id = 'champSelect';
    select.style.width = '300px';

    // Option par défaut "Choisir une ville" non sélectionnable
    const defaultOption = new Option('Choisir une ville', '');
    defaultOption.disabled = true;
    defaultOption.selected = true;
    select.add(defaultOption);

    const option1 = new Option('Aulnay sous bois', 'Aulnay sous bois');
    const option2 = new Option('Bondy', 'Bondy');
    const option3 = new Option('Sevran', 'Sevran');
    select.add(option1);
    select.add(option2);
    select.add(option3);
    champContainer.appendChild(select);
    buttonValidateOrder.classList.remove('d-none');
    selectedLocation.textContent = location || ''; // Utiliser la valeur enregistrée ou une chaîne vide par défaut

    // Restaurer la sélection depuis le cookie si disponible
    const savedOption = getCookie('selectedOption');
    if (savedOption && savedOption === 'delivery') {
      select.value = savedOption;
      const selectedOption = select.options[select.selectedIndex];
      selectedLocation.style.color = 'white';
      selectedLocation.textContent = 'Délai de livraison pour : ' + selectedOption.text + ' 40min';
    }

    // Écouter l'événement de changement du menu déroulant
    select.addEventListener('change', function() {
      const selectedOption = select.options[select.selectedIndex];
      selectedLocation.style.color = 'white';
      selectedLocation.textContent = 'Délai de livraison pour : ' + selectedOption.text + ' 40min';

      // Sauvegarder la sélection dans un cookie
      setCookie('selectedOption', 'delivery', 7); // Le cookie expire après 7 jours
      setCookie('selectedLocation', 'Délai de livraison pour : ' + selectedOption.text + ' 40min', 7); // Sauvegarder la valeur de l'emplacement dans le cookie
    });
  }
}
