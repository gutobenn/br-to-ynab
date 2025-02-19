# br-to-ynab

## Como reconfigurar certificado
1. Abrir terminal dentro nesta pasta e rodar o comando `pynubank`.
2. Depois de gerar o certificado (cert.p12), rodar o comando `base64 -i cert.p12 -o cert_encoded.txt`
3. Copiar o conteúdo do cert_encoded.txt para a variável dentro do arquivo br-to-ynab/br-to-ynab.json, e em seguida excluir o arquivo cert_encoded.txt
4. Rodar o script e checar se carregou certinho.


[![codecov](https://codecov.io/gh/andreroggeri/br-to-ynab/branch/main/graph/badge.svg?token=PK9LFN24FE)](https://codecov.io/gh/andreroggeri/br-to-ynab)

Sincronize seus gastos dos seus bancos para o YNAB automaticamente (Sucessor do [nubank-sync-ynab](https://github.com/andreroggeri/nubank-sync-ynab))

### Instituições Financeiras Suportadas

Esse projeto foi criado durante o meu tempo livre e só consegui implementar os bancos que tenho conta. Caso seu banco
não seja suportado, PRs são bem-vindas.

| Instituição | Produto           | Biblioteca      | Observação                            |
| ----------- | ----------------- | --------------- | ------------------------------------- |
| Nubank      | Conta corrente    | [pynubank][1]   |                                       |
| Nubank      | Cartão de crédito | [pynubank][1]   |                                       |
| Bradesco    | Conta corrente    | [pybradesco][2] | Últimos 90 dias                       |
| Bradesco    | Cartão de Crédito | [pybradesco][2] | Fatura aberta + Última fatura fechada |

[1]: https://github.com/andreroggeri/pynubank
[2]: https://github.com/andreroggeri/pybradesco

## Como funciona

Este script utiliza bibliotecas que permitem acesso aos extratos bancários e
o [ynab-sdk](https://github.com/andreroggeri/ynab-sdk-python)
para sincronizar as informações entre os sistemas.

Como alguns bancos podem precisar de um segundo fator de autenticação, o processo pode precisar de interação humana,
impedindo um processo 100% automatizado.

## Instalando
**TBD**

## Configuração inicial

Antes de iniciar a sincronização, é necessário configurar todas as contas que serão sincronizadas.

Para isso execute o comando `br-to-ynab --configure` e siga o passo a passo para configurar todas as contas.

Após isso será gerado um arquivo `br-to-ynab.json` com todos os parâmetros informados (Guarde em local seguro pois ele contém todas as credenciais).

## Sincronizando

Para iniciar a sincronização basta executar o comando `br-to-ynab --sync`.

Caso queira verificar quais transações serão importadas é possível informar o parâmetro `--dry` 
que ira exibir os dados no terminal mas não importará no YNAB.

## Testes

**TBD**

## Contribua

Se você tem alguma idéia para melhorar esse app, abra sua PR e contribua para esse projeto !
