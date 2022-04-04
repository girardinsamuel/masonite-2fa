"""CreateTwofabackupcodesTable Migration."""
from masoniteorm.migrations import Migration


class CreateTwofabackupcodesTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("twofa_backup_codes") as table:
            table.increments("id")
            table.string("code")
            table.boolean("used").default(False)
            table.integer("user_id").unsigned()
            table.foreign("user_id").references("id").on("users")
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("twofa_backup_codes")
