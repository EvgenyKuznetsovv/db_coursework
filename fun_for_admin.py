from main import connection, cursor
from fun_for_login import validate_input
from tabulate import tabulate


def view_all_promotions():
    try:
        cursor.execute("SELECT * FROM Promotions")
        promotions = cursor.fetchall()

        if promotions:
            table = [
                [promotion[0], promotion[1], f"{promotion[2]}%"]
                for promotion in promotions
            ]
            headers = ["ID", "Описание", "Скидка"]

            print(tabulate(table, headers=headers, tablefmt="grid"))
        else:
            print("Нет доступных акций.")
    except Exception as e:
        print(f"Ошибка при получении акций: {e}")


def add_promotion():
    description = validate_input("Введите описание: ")
    while True:
        discount_percentage = validate_input("Введите размер скидки: ")
        try:
            if 0 <= int(discount_percentage) <= 100:
                break
            else:
                print("Скидка должна быть от 0 до 100")
        except:
            print("Ошибка ввода")
            return

    cursor.execute("INSERT INTO Promotions (description, discount_percentage) VALUES (%s, %s)",
                    (description, discount_percentage))
    connection.commit()
    print("Акция успешно добавлена.")


def edit_promotion():
    promotion_id = validate_input("Введите ID: ")
    new_description = validate_input("Введите новое описание: ")
    while True:
        new_discount_percentage = validate_input("Введите новый размер скидки: ")
        try:
            if 0 <= int(new_discount_percentage) <= 100:
                break
            else:
                print("Скидка должна быть от 0 до 100")
        except:
            print("Ошибка ввода")
            return

    # Проверка существования акции с указанным ID
    cursor.execute("SELECT * FROM Promotions WHERE id = %s", (promotion_id,))
    existing_promotion = cursor.fetchone()

    if existing_promotion:
        cursor.execute("UPDATE Promotions SET description = %s, discount_percentage = %s WHERE id = %s",
                       (new_description, new_discount_percentage, promotion_id))
        connection.commit()

        print("Акция успешно отредактирована.")
    else:
        print("Акция с указанным ID не существует.")


def delete_promotion():
    promotion_id = validate_input("Введите ID: ")

    # Проверка существования акции с указанным ID
    cursor.execute("SELECT * FROM Promotions WHERE id = %s", (promotion_id,))
    existing_promotion = cursor.fetchone()

    try:
        if existing_promotion:
            cursor.execute("DELETE FROM Promotions WHERE id = %s", (promotion_id,))
            connection.commit()
            print("Акция успешно удалена.")
        else:
            print("Акция с указанным ID не существует.")
    except:
        print("Ошибка удаления!")


def view_all_books():
    try:
        cursor.execute("""
            SELECT 
                B.id AS book_id,
                B.book_title,
                A.name AS author_name,
                P.name AS publisher_name,
                G.name AS genre_name,
                B.price,
                B.quantity,
                B.average_mark
            FROM 
                Books B
                LEFT JOIN Authors_and_Books AB ON B.id = AB.book_id
                LEFT JOIN Authors A ON AB.author_id = A.id
                LEFT JOIN Publishers P ON B.publisher_id = P.id
                LEFT JOIN Books_and_Genres BG ON B.id = BG.book_id
                LEFT JOIN Genres G ON BG.genre_id = G.id
        """)
        books = cursor.fetchall()

        if books:
            table = [
                [
                    book[0],
                    book[1],
                    book[2],
                    book[3],
                    book[4],
                    f"{book[5]:.2f}",
                    book[6],
                    f"{book[7]:.1f}" if book[7] is not None else "N/A"
                ]
                for book in books
            ]

            headers = ["ID", "Название", "Автор", "Издатель", "Жанр", "Цена", "Количество", "Средняя оценка"]

            print(tabulate(table, headers=headers, tablefmt="grid"))
        else:
            print("Нет доступных книг.")
    except Exception as e:
        print(f"Ошибка при получении данных о книгах: {e}")


def add_book():
    book_title = validate_input("Введите название книги: ")
    try:
        quantity = int(validate_input("Введите кол-во книг: "))
        price = int(validate_input("Введите цену: "))
        publisher_id = int(validate_input("Введите id издательства: "))
        promotion_id = int(validate_input("Введите id акции: "))
        if (quantity < 1) or (price < 1) or (publisher_id < 1) or (promotion_id < 1 ):
            print("Ошибка ввода")
            return
    except:
        print("Ошибка ввода")
        return

    if not is_publisher_id_valid(publisher_id):
        print(f"Ошибка: Издательство с ID {publisher_id} не существует.")
        return

    if not is_promotion_id_valid(promotion_id):
        print(f"Ошибка: Акция с ID {promotion_id} не существует.")
        return

    try:
        cursor.callproc("AddBook", (book_title, price, quantity, publisher_id, promotion_id))
        connection.commit()
        print("Книга успешно добавлена.")
    except:
       print("Ошибка добавления")


def is_publisher_id_valid(publisher_id):
    try:
        cursor.execute("SELECT id FROM Publishers WHERE id = %s", (publisher_id,))
        result = cursor.fetchone()
        return result is not None
    except:
        print("тест!!!")
        return False


def is_promotion_id_valid(promotion_id):
    try:
        cursor.execute("SELECT id FROM Promotions WHERE id = %s", (promotion_id,))
        result = cursor.fetchone()
        return result is not None
    except:
        return False


def edit_book():
    new_title = validate_input("Введите название книги: ")
    try:
        book_id = int(validate_input("Введите id книги: "))
        new_quantity = int(validate_input("Введите кол-во книг: "))
        new_price = int(validate_input("Введите цену: "))
        new_publisher_id = int(validate_input("Введите id издательства: "))
        new_promotion_id = int(validate_input("Введите id акции: "))
        if (new_quantity < 1) or (new_price < 1) or (new_publisher_id < 1) or (new_promotion_id < 1) or (book_id < 1):
            print("Ошибка ввода")
            return
    except:
        print("Ошибка ввода")
        return

    if not is_publisher_id_valid(new_publisher_id):
        print(f"Ошибка: Издательство с ID {new_publisher_id} не существует.")
        return

    if not is_promotion_id_valid(new_promotion_id):
        print(f"Ошибка: Акция с ID {new_promotion_id} не существует.")
        return

    try:
        # Проверка существования книги с указанным ID
        cursor.execute("SELECT * FROM Books WHERE id = %s", (book_id,))
        existing_book = cursor.fetchone()

        if existing_book:
            sql_query = """
                    UPDATE Books
                    SET 
                        book_title = %s,
                        price = %s,
                        quantity = %s,
                        publisher_id = %s,
                        promotion_id = %s
                    WHERE id = %s
                    """
            cursor.execute(sql_query, (new_title, new_price, new_quantity, new_publisher_id, new_promotion_id, book_id))

            # Подтверждение изменений в базе данных
            connection.commit()

            print("Книга успешно отредактирована.")
        else:
            print("Книга с указанным ID не существует.")

    except:
        print("Ошибка обновления")


def delete_book():
    try:
        book_id = int(validate_input("Введите id книги"))
        if book_id < 1:
            print("Ошибка ввода")
            return
    except:
        print("Ошибка ввода")
        return

    try:
        cursor.execute("SELECT * FROM Books WHERE id = %s", (book_id,))
        existing_book = cursor.fetchone()
        if existing_book:
            cursor.execute("DELETE FROM Books WHERE id = %s", (book_id,))
            connection.commit()
            print("Книга успешно удалена.")
        else:
            print("Книга с указанным ID не существует.")

    except:
        print("Ошибка удаления")


def view_all_publishers():
    try:
        cursor.execute("""
            SELECT id, name, country
            FROM Publishers
        """)
        publishers = cursor.fetchall()

        if publishers:
            table = [
                [publisher[0], publisher[1], publisher[2]]
                for publisher in publishers
            ]
            headers = ["ID", "Название", "Страна"]

            print(tabulate(table, headers=headers, tablefmt="grid"))
        else:
            print("Нет доступных издательств.")
    except Exception as e:
        print(f"Ошибка при получении данных об издательствах: {e}")


def add_publisher():
    name = validate_input("Введите название: ")
    country = validate_input("Введите страну: ")
    try:
        cursor.execute("""
            INSERT INTO Publishers (name, country) 
            VALUES (%s, %s)
        """, (name, country))
        connection.commit()
        print("Издательство успешно добавлено.")
    except Exception as e:
        print(f"Ошибка при добавлении издательства: {e}")


def edit_publisher():
    try:
        publisher_id = int(validate_input("Введит id: "))
        new_name = validate_input("Введите название: ")
        new_country = validate_input("Введите страну: ")
    except:
        print("Ошибка редкатирования")
        return

    try:
        cursor.execute("SELECT * FROM Publishers WHERE id = %s", (publisher_id,))
        existing_publisher = cursor.fetchone()

        if existing_publisher:
            cursor.execute("""
                UPDATE Publishers 
                SET name = %s, country = %s 
                WHERE id = %s
            """, (new_name, new_country, publisher_id))
            connection.commit()
            print("Издательство успешно отредактировано.")
        else:
            print("Издательство не найдено.")
    except Exception as e:
        print(f"Ошибка при редактировании издательства: {e}")


def delete_publisher():
    try:
        publisher_id = int(validate_input("Введит id: "))
    except:
        print("Ошибка удаления")
        return
    try:
        cursor.execute("SELECT * FROM Publishers WHERE id = %s", (publisher_id,))
        existing_publisher = cursor.fetchone()

        if existing_publisher:
            cursor.execute("""
                DELETE FROM Publishers 
                WHERE id = %s
            """, (publisher_id,))
            connection.commit()
            print("Издательство успешно удалено.")
        else:
            print("Издательство не найдено.")
    except Exception as e:
        print(f"Ошибка при удалении издательства: {e}")


def add_genre():
    name = validate_input("Введите название жанра: ")
    try:
        cursor.execute("""
            INSERT INTO Genres (name) 
            VALUES (%s)
        """, (name,))
        connection.commit()
        print("Жанр успешно добавлен.")
    except Exception as e:
        print(f"Ошибка при добавлении жанра: {e}")


def edit_genre():
    try:
        genre_id = int(validate_input("Введит id: "))
        new_name = validate_input("Введите новое название: ")
    except:
        print("Ошибка редактирования")
        return
    try:
        # Проверяем существование жанра
        cursor.execute("SELECT * FROM Genres WHERE id = %s", (genre_id,))
        existing_genre = cursor.fetchone()

        if existing_genre:
            cursor.execute("""
                UPDATE Genres 
                SET name = %s 
                WHERE id = %s
            """, (new_name, genre_id))
            connection.commit()
            print("Жанр успешно отредактирован.")
        else:
            print("Жанр не найден.")
    except Exception as e:
        print(f"Ошибка при редактировании жанра: {e}")


def delete_genre():
    try:
        genre_id = int(validate_input("Введит id: "))
    except:
        print("Ошибка удаления")
        return
    try:
        # Проверяем существование жанра
        cursor.execute("SELECT * FROM Genres WHERE id = %s", (genre_id,))
        existing_genre = cursor.fetchone()

        if existing_genre:
            cursor.execute("""
                DELETE FROM Genres 
                WHERE id = %s
            """, (genre_id,))
            connection.commit()
            print("Жанр успешно удален.")
        else:
            print("Жанр не найден.")
    except Exception as e:
        print(f"Ошибка при удалении жанра: {e}")


def view_all_genres():
    try:
        cursor.execute("""
            SELECT id, name
            FROM Genres
        """)
        genres = cursor.fetchall()

        if genres:
            table = [[genre[0], genre[1]] for genre in genres]
            headers = ["ID", "Название"]

            print(tabulate(table, headers=headers, tablefmt="grid"))
        else:
            print("Нет доступных жанров.")
    except Exception as e:
        print(f"Ошибка при получении данных о жанрах: {e}")


def view_all_authors():
    try:
        cursor.execute("""
            SELECT id, name, country
            FROM Authors
        """)
        authors = cursor.fetchall()

        if authors:
            table = [[author[0], author[1], author[2]] for author in authors]
            headers = ["ID", "Имя", "Страна"]

            print(tabulate(table, headers=headers, tablefmt="grid"))
        else:
            print("Нет доступных авторов.")
    except Exception as e:
        print(f"Ошибка при получении данных об авторах: {e}")


def add_author():
    name = validate_input("Введите имя")
    country = validate_input("Введите страну")
    try:
        cursor.execute("""
            INSERT INTO Authors (name, country) 
            VALUES (%s, %s)
        """, (name, country))
        connection.commit()
        print("Автор успешно добавлен.")
    except Exception as e:
        print(f"Ошибка при добавлении автора: {e}")


def edit_author():
    try:
        author_id = int(validate_input("Введит id: "))
        new_name = validate_input("Введите имя: ")
        new_country = validate_input("Введите страну: ")
    except:
        print("Ошибка редактирования")
        return

    try:
        # Проверяем существование автора
        cursor.execute("SELECT * FROM Authors WHERE id = %s", (author_id,))
        existing_author = cursor.fetchone()

        if existing_author:
            cursor.execute("""
                UPDATE Authors 
                SET name = %s, country = %s 
                WHERE id = %s
            """, (new_name, new_country, author_id))
            connection.commit()
            print("Автор успешно отредактирован.")
        else:
            print("Автор не найден.")
    except Exception as e:
        print(f"Ошибка при редактировании автора: {e}")


def delete_author():
    try:
        author_id = int(validate_input("Введит id: "))
    except:
        print("Ошибка удаления")
        return
    try:
        # Проверяем существование автора
        cursor.execute("SELECT * FROM Authors WHERE id = %s", (author_id,))
        existing_author = cursor.fetchone()

        if existing_author:
            cursor.execute("""
                DELETE FROM Authors 
                WHERE id = %s
            """, (author_id,))
            connection.commit()
            print("Автор успешно удален.")
        else:
            print("Автор не найден.")
    except Exception as e:
        print(f"Ошибка при удалении автора: {e}")


def view_all_logs():
    try:
        cursor.execute("""
            SELECT 
                Log.id AS log_id,
                Log.message,
                User.login AS customer_login
            FROM 
                Log
                LEFT JOIN User ON Log.id_customer = User.id_customer
        """)
        logs = cursor.fetchall()

        if logs:
            table = [[log[0], log[1], log[2]] for log in logs]
            headers = ["ID", "Сообщение", "Логин Клиента"]

            print(tabulate(table, headers=headers, tablefmt="grid"))
        else:
            print("Логи отсутствуют.")
    except Exception as e:
        print(f"Ошибка при чтении логов: {e}")


def view_all_reviews():
    try:
        cursor.execute("""
            SELECT 
                R.id, 
                R.description, 
                R.mark, 
                B.book_title, 
                U.login
            FROM 
                Reviews R
                LEFT JOIN Books B ON R.book_id = B.id
                LEFT JOIN User U ON R.customer_id = U.id_customer
        """)
        reviews = cursor.fetchall()

        if reviews:
            table = [[review[0], review[1], review[2], review[3], review[4]] for review in reviews]
            headers = ["ID", "Описание", "Оценка", "Название Книги", "Логин Клиента"]

            print(tabulate(table, headers=headers, tablefmt="grid"))
        else:
            print("Нет доступных отзывов.")
    except Exception as e:
        print(f"Ошибка при чтении отзывов: {e}")


def delete_review():
    try:
        review_id = int(validate_input("Введит id: "))
    except:
        print("Ошибка удаления")
        return
    try:
        cursor.execute("SELECT * FROM Reviews WHERE id = %s", (review_id,))
        existing_review = cursor.fetchone()

        if existing_review:
            cursor.execute("""
                DELETE FROM Reviews 
                WHERE id = %s
            """, (review_id,))
            connection.commit()
            print("Отзыв успешно удален.")
        else:
            print("Отзыв не найден.")
    except Exception as e:
        print(f"Ошибка при удалении отзыва: {e}")


def view_all_users():
    try:
        cursor.execute("""
            SELECT 
                user.id AS user_id, 
                user.login, 
                customers.surname, 
                customers.name, 
                customers.patronymic, 
                customers.telephone, 
                customers.email
            FROM 
                user
            INNER JOIN 
                customers 
            ON 
                user.id_customer = customers.id
        """)

        results = cursor.fetchall()

        table = [
            [row[0], row[1], row[2], row[3], row[4], row[5], row[6]]
            for row in results
        ]
        headers = ["User ID", "Login", "Surname", "Name", "Patronymic", "Telephone", "Email"]

        print(tabulate(table, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"Ошибка при просмотре клиентов: {e}")


def delete_user():
    try:
        user_id = int(validate_input("Введите ID пользователя: "))
    except ValueError:
        print("Ошибка: некорректный ввод ID.")
        return

    try:
        cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            id_customer = existing_user[3]

            cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
            connection.commit()

            cursor.execute("DELETE FROM customers WHERE id = %s", (id_customer,))
            connection.commit()

            print(f"Пользователь успешно удален")
        else:
            print("Пользователь с таким ID не найден.")
    except Exception as e:
        print(f"Ошибка при удалении пользователя: {e}")


def view_orders():
    try:
        cursor.execute("""
            SELECT 
                O.id AS order_id,
                B.book_title,
                C.surname AS customer_surname,
                D.status AS delivery_status,
                O.order_date AS order_date
            FROM 
                Orders O
                JOIN Books B ON O.book_id = B.id
                JOIN Order_history OH ON O.history_id = OH.id
                JOIN Customers C ON OH.customer_id = C.id
                JOIN Delivery_status D ON O.status_id = D.id
        """)
        orders = cursor.fetchall()

        if orders:
            table = [[order[0], order[1], order[2], order[3], order[4]] for order in orders]
            headers = ["ID заказа", "Название книги", "Фамилия клиента", "Статус доставки", "Дата заказа"]
            print("Список заказов:")
            print(tabulate(table, headers=headers, tablefmt="grid"))
        else:
            print("Нет доступных заказов.")
    except Exception as e:
        print(f"Ошибка при чтении заказов: {e}")


def change_delivery_status():
    try:
        cursor.execute("SELECT id, status FROM Delivery_status")
        statuses = cursor.fetchall()

        order_id = input("Введите ID заказа для обновления статуса: ")

        if statuses:
            print("Доступные статусы доставки:")
            for status in statuses:
                print(f"ID: {status[0]}, Статус: {status[1]}")

            cursor.execute("SELECT id FROM Orders WHERE id = %s", (order_id,))
            order = cursor.fetchone()

            if order:
                status_id = input("Введите ID статуса для обновления: ")
                cursor.execute("SELECT id FROM Delivery_status WHERE id = %s", (status_id,))
                status = cursor.fetchone()

                if status:
                    cursor.execute("""
                        UPDATE Orders
                        SET status_id = %s
                        WHERE id = %s
                    """, (status_id, order_id))
                    connection.commit()
                    print(f"Статус заказа {order_id} успешно обновлен.")
                else:
                    print("Такого статуса не существует.")
            else:
                print(f"Заказ с ID {order_id} не найден.")
        else:
            print("Нет доступных статусов доставки.")
    except Exception as e:
        print(f"Ошибка при изменении статуса доставки: {e}")


def delete_order():
    try:
        order_id = input("Введите ID заказа для удаления: ")

        cursor.execute("SELECT id FROM Orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()

        if order:
            cursor.execute("DELETE FROM Orders WHERE id = %s", (order_id,))
            connection.commit()
            print(f"Заказ с ID {order_id} успешно удален.")
        else:
            print(f"Заказ с ID {order_id} не найден.")
    except Exception as e:
        print(f"Ошибка при удалении заказа: {e}")









