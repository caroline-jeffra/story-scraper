<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Story extends Model
{
    protected $table = 'story';

    protected $fillable = [
        'title',
        'url',
        'content',
        'author_id',
        'issue_id',
    ];

    public function author(): BelongsTo
    {
        return $this->BelongsTo(Author::class, 'author_id');
    }

    public function issue(): BelongsTo
    {
        return $this->belongsTo(Issue::class, 'issue_id');
    }
}
