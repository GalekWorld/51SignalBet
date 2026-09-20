# Settlement

`SettlementService` bloquea el bet pendiente, crea un único `SettlementEvent`,
actualiza su estado y acredita el bankroll cuando corresponde. Repetir el mismo
settlement devuelve el evento existente; intentar cambiar el resultado produce
`SettlementConflict`.

La liquidación asume que el stake ya fue debitado del ledger al registrar la bet:
una victoria acredita `stake * odds`, mientras que `VOID` y `PUSH` devuelven el
stake. Una derrota no crea una transacción adicional.
