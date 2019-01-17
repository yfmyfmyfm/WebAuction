-- description: Constraint 14

PRAGMA foreign_keys = ON;

drop trigger if exists trigger3;

create trigger trigger3
  before insert on Bids
  for each row
    when EXISTS (
        SELECT 1
        FROM Items i
        WHERE New.ItemID = i.ItemID
          AND 
          (
              i.Number_of_Bids > 0 AND NEW.Amount <= i.Currently
              OR
              i.Number_of_Bids == 0 AND NEW.AMOUNT < i.Currently
          )
      )
  begin
    SELECT raise(rollback, ‘Trigger3_Failed’);
  end;
