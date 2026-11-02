Файл-заготовка пуст. Посмотрю структуру проекта, чтобы понять, есть ли сервисы и модели.
Проект — синтетический фиксчер без сборочных файлов (pom.xml/gradle отсутствуют), есть только заготовка `OrderController.java`. По стековым правилам контроллер должен быть тонким, логика — в сервисе, внедрение — через конструктор. Создам контроллер и минимальный сервис с моделью.
Готово. Добавлен endpoint `GET /orders` в соответствии со стековыми правилами `.ai-standards/references/stacks/spring.md`:

- `src/main/java/app/OrderController.java` — тонкий контроллер: только маппинг `@GetMapping("/orders")`, логика делегируется в сервис; внедрение через конструктор.
- `src/main/java/app/OrderService.java` — новый `@Service` с методом `findAll()` (хранилище в памяти, `CopyOnWriteArrayList`, наружу отдаётся неизменяемая копия).
- `src/main/java/app/Order.java` — record-модель `Order(Long id, String status)`.

Замечание по проверке: в проекте нет pom.xml/gradle, поэтому компиляцию проверить нельзя — файлы написаны по стандартной структуре Spring (package `app`, jakarta-независимые аннотации `org.springframework.web.bind.annotation.*`), но сборку и запуск нужно выполнить в окружении с зависимостями Spring.