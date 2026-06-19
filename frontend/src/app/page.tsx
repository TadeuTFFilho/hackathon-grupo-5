// Página inicial — ponto de entrada do app
// Bia: fluxo de entrada (formulário)
// Tadeu: dashboard de resultados

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">💸 DebtFree AI</h1>
      <p className="text-gray-600 text-lg text-center max-w-md mb-8">
        Entenda suas dívidas, conheça seus direitos e negocie com segurança.
      </p>
      <a
        href="/onboarding"
        className="bg-blue-600 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:bg-blue-700 transition"
      >
        Começar agora
      </a>
    </main>
  );
}
