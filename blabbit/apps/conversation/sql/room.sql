/*
 * Custom SQL that is executed just after the CREATE TABLE statements when you
 * run syncdb.
 * Will use this to add in the configurations that are expected by ejabberd's
 * `muc_room` table schema
 */

-- Django standard has us avoid using NULL on string-based fields such as
--   CharField and TextField because empty string values will always be stored
--   as empty strings, not as NULL.
-- So for any such fields that are provided as an extension to ejabberd's schema
--   since ejabberd will not be setting them we shall have them default to ''
-- ref: https://docs.djangoproject.com/en/dev/ref/models/fields/#null
ALTER TABLE ONLY muc_room ALTER COLUMN subject SET DEFAULT '';
ALTER TABLE ONLY muc_room ALTER COLUMN photo   SET DEFAULT '';

ALTER TABLE ONLY muc_room ALTER COLUMN last_modified SET DEFAULT now();
ALTER TABLE ONLY muc_room ALTER COLUMN likes_count SET DEFAULT 0;

-- ejabberd's `muc_room` table schema has this default
ALTER TABLE ONLY muc_room ALTER COLUMN created_at SET DEFAULT now();

-- this constraint comes right out of ejabberd's pg.sql
-- https://github.com/processone/ejabberd/blob/master/sql/pg.sql
CREATE UNIQUE INDEX i_muc_room_name_host ON muc_room USING btree (name, host);
