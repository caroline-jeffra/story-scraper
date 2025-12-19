<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasOneOrMany;

class Author extends Model
{
    protected $table = 'author';

    protected $fillable = [
        'name',
    ];

    public function story(): HasOneOrMany
    {
        return $this->hasOneOrMany(Story::class, 'story_id');
    }
}
