<?php

use Illuminate\Support\Facades\Route;

/* Route::get('/', function () { */
/*     return view('welcome'); */
/* }); */

/* Route::view('/', 'welcome')->name('home'); */

/* Route::get('/product/{id}', function(string $id) { */
/*     return "This product ID is: {$id}"; */
/* })->name('products'); */

Route::prefix('admin')->name('admin.')->group(function () {
    Route::get('dashboard', fn () => 'Dashboard')->name('dashboard');
    Route::get('create', fn () => 'Create')->name('create');
    Route::get('delete', fn () => 'Delete')->name('delete');
});

Route::group([
    'prefix' => 'teacher',
    'as'     => 'teacher.'
], function () {
    Route::get('dashboard', fn () => 'Dashboard')->name('dashboard');
    Route::get('create', fn () => 'Create')->name('create');
    Route::get('delete', fn () => 'Delete')->name('delete');
});

Route::get('/', fn () =>
    redirect()->route('teacher.dashboard')
);


Route::get('/info', fn () => 'A' )->name('info');

Route::get('/about', fn () => redirect()->route('info'));

Route::redirect('/aboutt', 'info');


// Route::get('/user', [UserController::class, 'index']);
