# OwlNest

# на русском ниже!!


Hello! This is my small Reddit-like project where I implemented the following features:

1: User registration, login, and permission system for different types of users.

2: Post creation, and I optimized the HTML code using include.

3: Ability to attach images, videos, and YouTube video links (using django-embed-video).

4: Post rating system, which is displayed on the user's karma.

5: Subscription to tags and users.

6: Search system for tags, post titles, users, and keywords in the post content.

7: Commenting system.

8: Display of the best posts for the day, week, and all time.

9: Ability to edit and delete everything with the necessary permissions.

10: User profile (posts, user information, avatar), subscriptions (all user subscriptions are displayed).

I also worked on optimizing the readability of the code in urls, templates, and views. 
I also used the split settings technology, which allows you to ignore the settings file that should not be included in the repository. However, they look like this:

DATABASES = {
'default': {
'ENGINE': 'django.db.backends.postgresql',
'NAME': os.environ.get('DB_NAME'),
'USER': os.environ.get('DB_USER'),
'PASSWORD': os.environ.get('DB_PASSWORD'),
'HOST': os.environ.get('DB_HOST'),
'PORT': os.environ.get('DB_PORT'),
}
}

Challenges I faced during development may seem funny to an experienced developer, but it's normal in learning. It gave me a lot of understanding of different details and the depth of development:

1: Dockerfile, docker-compose with PostgreSQL. The problems were with the proper connection of web and db services and correct display.

2: Everything related to static files and uploads at different stages. Display and connection through the same Docker. 
I understand that this is a production problem on a local machine, and all this routine works differently on a finished project.

3: Split settings. I set it up for the first time, and everything that could go wrong went wrong.

That's it in a nutshell. You can learn more by checking out the repository.

I wanted to create an API and Nginx, but I decided to make a separate project to showcase it.

# Have a nice day!

![screen](https://github.com/EricReinhart/OwlNest/assets/109595175/0329ff48-62f0-4680-827e-b1367580d727)


Привет! Это мой небольшой проект типа реддита. В нём я реализовал следующие функции:

1: регистрация, логирование, система разрешений для различного рода пользователей.

2: Создание постов + прошу заметить оптимизацию HTML кода, через include

3: Возможность прикреплять картинки, видео и ссылки на ютуб видео(django-embed-video
)

4: Система рейтинга постов, которая отображается на карме пользователя

5: Возможность подписываться на теги и пользователей

6: Система поиска по тегам, названию постов, пользователям, ключевым словам в контенте самого поста

7: комментирование

8: Отображение лучших постов за день, неделю и за всё время

9: Возможность редактирования и удаления всего и вся, при должных правах.

10: Профиль пользователя(посты, информация о пользователе, аватарка), подписки(отображаются все подписки пользователя)

Прошу обратить внимание на работу с оптимизацией читаемости кода в urls, templates, views. 
Так же я использовал технологию split settings, которая позволяет кинуть в gitignore файл с настройками, которые не должны попасть в репозитории. Правда и там они выглядят как то так:

DATABASES = {
'default': {
'ENGINE': 'django.db.backends.postgresql',
'NAME': os.environ.get('DB_NAME'),
'USER': os.environ.get('DB_USER'),
'PASSWORD': os.environ.get('DB_PASSWORD'),
'HOST': os.environ.get('DB_HOST'),
'PORT': os.environ.get('DB_PORT'),
}
}

Задачи с которыми я столкнулся во время разработки, для опытного разработчика, возможно, могли бы показаться привычными, но для неопытного разработчика могут стать настоящими проблемами. Очень много дало понимания разных мелочей и глубины разработки:
1 dockerfile, dockercompose через postgresql. Проблемы заключались в нормальном подключении web и db сервисов между собой и правильным отображением.
2 Всё что связано со staticfiles и uploads, на разных этапах. Отображение, подключение через тот же докер. 
При этом понимаю, что это проблемы продакшена на локальной машине, вся эта рутина работает по другому на уже готовом проекте.
3 split settings. Первый раз настраивал это всё. И всё что могло пойти не так, шло не так =)

кратко это всё. Остальное можете изучить уже в репозитории.

Было желание сделать и Api с ngninx, но решил, что вынесу пример работы с api в отдельный проект.

Хорошего дня!
