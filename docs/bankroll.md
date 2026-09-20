# Bankroll virtual

El saldo no se almacena como una mutación directa: se reconstruye sumando el
ledger de `BankrollTransaction`. Cada operación exige una `idempotency_key` única
por banca, por lo que repetir una solicitud no duplica dinero virtual.

Los withdrawals y stakes negativos se rechazan si dejarían el saldo por debajo de
cero. El sistema no conecta con cuentas reales ni ejecuta apuestas.
