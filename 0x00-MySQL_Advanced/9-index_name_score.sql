-- script that creates an index idx_name_first_score on the table
-- names and the first letter of name and the score

DELIMITER $$ ;
CREATE TRIGGER resets_valid_email BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
	IF NEW.email != OLD.email THEN
		SET NEW.valid_email = 0;
	END IF;
END;
DELIMITER ;