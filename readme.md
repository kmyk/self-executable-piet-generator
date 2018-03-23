# "self-executable Piet" generator

This generates something like self-extracting archive for Piet.

## example

![](https://raw.githubusercontent.com/kmyk/self-executable-piet-generator/master/example/helloworld.png)

execute:

```
$ bash example/helloworld.png 2>/dev/null
Hello, World!

$ npiet example/helloworld.png
Hello, World!
```

generate:

```
$ python3 main.py original.image > self-executable.png
```

## license

-   `Interpreter.pm` under the same license that comes with Perl
    -   the interpreter part of `Interpreter.pm` is Marc Majcher's <http://search.cpan.org/~majcher/Piet-Interpreter-0.03/>
-   `main.py` is under the MIT License
