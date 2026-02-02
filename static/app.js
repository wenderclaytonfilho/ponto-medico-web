async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch("/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username, password})
  });

  const data = await res.json();

  if (data.success) {
    location.href = data.role === "admin" ? "/admin" : "/dashboard";
  } else {
    document.getElementById("msg").innerText = data.message;
  }
}

async function registrar(tipo) {
  await fetch("/registrar_ponto", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({tipo})
  });
  carregar();
}

async function carregar() {
  const res = await fetch("/meus_registros");
  const dados = await res.json();
  const lista = document.getElementById("lista");
  if (!lista) return;

  lista.innerHTML = "";
  dados.forEach(r => {
    lista.innerHTML += `<li>${r.data} - ${r.tipo}</li>`;
  });
}

async function relatorio() {
  const res = await fetch("/relatorio");
  const dados = await res.json();
  const tabela = document.getElementById("tabela");

  dados.forEach(r => {
    tabela.innerHTML += `
      <tr>
        <td>${r.username}</td>
        <td>${r.tipo}</td>
        <td>${r.data}</td>
      </tr>`;
  });
}

carregar();
relatorio();
