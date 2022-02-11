CREATE TABLE IF NOT EXISTS passwordmanager (
                                        website text PRIMARY KEY,
                                        username text NOT NULL,
                                        password text,
                                        notes text
                                    );
