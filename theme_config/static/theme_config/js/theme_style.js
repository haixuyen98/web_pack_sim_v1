window.addEventListener("load", function () { 
  const colorInput = document.getElementById("favcolor"); 
  const textInput = document.getElementById("colorMenu"); 
 
  colorInput.addEventListener("input", function (event) { 
    const selectedColor = event.target.value; 
    // textInput.value = selectedColor; 
  }); 
 
  const colorListSim = document.getElementById("favcolorListSim"); 
  const textListSim = document.getElementById("colorListSim"); 
 
  colorListSim.addEventListener("input", function (event) { 
    const selectedColor = event.target.value; 
    textListSim.value = selectedColor; 
  }); 
 
  const colorSearch = document.getElementById("favcolorSearch"); 
  const textSearch = document.getElementById("colorSearch"); 
 
  colorSearch.addEventListener("input", function (event) { 
    const selectedColor = event.target.value; 
    textSearch.value = selectedColor; 
  }); 
 
  const colorHighlight = document.getElementById("favcolorHighlight"); 
  const textHighlight = document.getElementById("colorHighlight"); 
 
  colorHighlight.addEventListener("input", function (event) { 
    const selectedColor = event.target.value; 
    textHighlight.value = selectedColor; 
  }); 
 
  const colorBG = document.getElementById("favcolorBG"); 
  const textBG = document.getElementById("colorBG"); 
 
  colorBG.addEventListener("input", function (event) { 
    const selectedColor = event.target.value; 
    textBG.value = selectedColor; 
  }); 
 
  const colorBgMenu = document.getElementById("favcolorBgMenu"); 
  const textBgMenu = document.getElementById("colorBgMenu"); 
 
  colorBgMenu.addEventListener("input", function (event) { 
    const selectedColor = event.target.value; 
    textBgMenu.value = selectedColor; 
  }); 
 
  const colorTextMenu = document.getElementById("favcolorTextMenu"); 
  const textMenu = document.getElementById("colorTextMenu"); 
 
  colorTextMenu.addEventListener("input", function (event) { 
    const selectedColor = event.target.value; 
    textMenu.value = selectedColor; 
  }); 
});